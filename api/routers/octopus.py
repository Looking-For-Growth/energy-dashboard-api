import json
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from services.api_clients import OctopusService
from schemas.octopus import GridSupplyPointSchema, GSPPriceSchema

router = APIRouter(tags=["Octopus Energy"])

GSP_CONVERSION_TABLE = {
    1: "A",
    2: "B",
    3: "C",
    4: "D",
    5: "E",
    6: "F",
    7: "G",
    8: "H",
    9: "J",
    10: "K",
    11: "L",
    12: "M",
    13: "N",
    14: "P",
}

INV_GSP_CONVERSION_TABLE = {v: k for k, v in GSP_CONVERSION_TABLE.items()}


@router.get("/grid-supply-point/", response_model=list[GridSupplyPointSchema])
def list_grid_supply_points():
    service = OctopusService()
    gsp_data = service.get_grid_supply_points(format="json")
    return gsp_data.get("results", [])


@router.get("/grid-supply-point/by-postcode/")
def get_grid_supply_point_by_postcode(postcode: str = Query(default="SW1A1AA")):
    service = OctopusService()
    group_id = service.get_grid_supply_point_by_postcode(postcode=postcode)
    return {"group_id": group_id}


@router.get("/grid-supply-point-price/", response_model=list[GSPPriceSchema])
def list_gsp_prices(
    from_date: str = Query(...),
    to_date: str = Query(...),
    gsp: int = Query(default=1),
):
    try:
        parsed_from = datetime.strptime(from_date, "%Y-%m-%dT%H:%MZ")
        parsed_to = datetime.strptime(to_date, "%Y-%m-%dT%H:%MZ")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use ISO format (e.g., 2024-05-30T00:00Z)",
        )

    gsp_letter = GSP_CONVERSION_TABLE.get(gsp, gsp)

    service = OctopusService()
    price_data = service.get_gsp_price(gsp_letter, parsed_from, parsed_to)
    return price_data.get("results", [])


@router.get("/grid-supply-point-price/aggregated-prices/")
def aggregated_prices(
    from_date: str = Query(...),
    to_date: str = Query(...),
):
    try:
        parsed_from = datetime.strptime(from_date, "%Y-%m-%dT%H:%MZ")
        parsed_to = datetime.strptime(to_date, "%Y-%m-%dT%H:%MZ")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use ISO format (e.g., 2024-05-30T00:00Z)",
        )

    service = OctopusService()

    results = {}
    for gsp_id, gsp_letter in GSP_CONVERSION_TABLE.items():
        price_data = service.get_gsp_price(gsp_letter, parsed_from, parsed_to)
        results[gsp_id] = price_data.get("results", [])

    return results


@router.get("/grid-supply-point-price/quarterly-prices/")
def quarterly_prices_by_region(
    quarter: int = Query(...),
    year: int = Query(...),
):
    if quarter < 1 or quarter > 4:
        raise HTTPException(status_code=400, detail="Quarter must be between 1 and 4.")

    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    start_date = datetime(year, start_month, 1)
    end_date = datetime(year, end_month, 1)

    file_path = os.path.join(
        os.path.dirname(__file__), "../data/octopus_prices/energy_prices_gsp_quarters.json"
    )
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Data file not found.")

    with open(file_path, "r") as f:
        data = json.load(f)

    filtered_data = {}
    for region, prices in data.items():
        filtered_prices = []
        for month, price in prices.items():
            month_date = datetime.strptime(month, "%Y-%m")
            if start_date <= month_date <= end_date:
                filtered_prices.append(price)
        if filtered_prices:
            filtered_data[INV_GSP_CONVERSION_TABLE[region]] = filtered_prices

    return filtered_data
