import json
import os
from datetime import datetime, timedelta

from dateutil.parser import parse as parse_datetime
from fastapi import APIRouter, HTTPException, Query

from services.api_clients import CarbonIntensityService

router = APIRouter(tags=["Carbon Intensity"])

INDEX_DISPLAY = {
    "very low": "Very Low",
    "low": "Low",
    "moderate": "Moderate",
    "high": "High",
    "very high": "Very High",
}


def _normalise_datetime(dt_str: str | None) -> str | None:
    """Ensure datetime strings include seconds, e.g. '2026-03-26T16:00Z' -> '2026-03-26T16:00:00Z'."""
    if dt_str is None:
        return None
    try:
        parsed = parse_datetime(dt_str)
        return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        return dt_str


def _flatten_intensity_entry(entry: dict) -> dict:
    """Transform upstream API entry into the flat shape the old Django serializer returned.

    Upstream: {"from": "...", "to": "...", "intensity": {"actual": 200, "forecast": 195, "index": "moderate"}}
    Old API:  {"from_datetime": "...", "to_datetime": "...", "actual": 200, "forecast": 195, "index": "Moderate", "region": null, "postcode_prefix": null}
    """
    intensity = entry.get("intensity", {})
    raw_index = intensity.get("index", "moderate")
    return {
        "from_datetime": _normalise_datetime(entry.get("from")),
        "to_datetime": _normalise_datetime(entry.get("to")),
        "actual": intensity.get("actual"),
        "forecast": intensity.get("forecast"),
        "index": INDEX_DISPLAY.get(raw_index, raw_index),
        "region": None,
        "postcode_prefix": None,
    }


def _flatten_intensity_list(response: dict) -> list[dict]:
    """Extract data from upstream response and flatten each entry."""
    data = response.get("data", [])
    if isinstance(data, list):
        return [_flatten_intensity_entry(entry) for entry in data]
    return [_flatten_intensity_entry(data)]


def _flatten_stats(response: dict, from_time: str, to_time: str) -> dict:
    """Transform upstream stats into the shape the old Django serializer returned.

    Upstream: {"data": [{"from": "...", "to": "...", "intensity": {"min": 50, "max": 300, "average": 175.5}}]}
    Old API:  {"from_datetime": "...", "to_datetime": "...", "min_intensity": 50, "max_intensity": 300, "average_intensity": 175.5, "block_hours": null}
    """
    data = response.get("data", [])
    if isinstance(data, list) and data:
        entry = data[0]
        intensity = entry.get("intensity", {})
    else:
        intensity = data if isinstance(data, dict) else {}
    return {
        "from_datetime": from_time,
        "to_datetime": to_time,
        "min_intensity": intensity.get("min"),
        "max_intensity": intensity.get("max"),
        "average_intensity": intensity.get("average"),
        "block_hours": None,
    }


def _flatten_generation_mix_entry(entry: dict) -> dict:
    """Transform upstream generation mix entry into the shape the old Django serializer returned.

    Upstream: {"from": "...", "to": "...", "generationmix": [{"fuel": "coal", "perc": 2.5}, ...]}
    Old API:  {"from_datetime": "...", "to_datetime": "...", "fuel_mix": {"coal": 2.5, ...}}
    """
    gen_mix = entry.get("generationmix", [])
    fuel_mix = {item["fuel"]: item["perc"] for item in gen_mix}
    return {
        "from_datetime": _normalise_datetime(entry.get("from")),
        "to_datetime": _normalise_datetime(entry.get("to")),
        "fuel_mix": fuel_mix,
    }


@router.get("/carbon-intensity/")
def list_carbon_intensity(
    from_dt: str = Query(None, alias="from"),
    to_dt: str = Query(None, alias="to"),
    region_id: int = Query(None),
    postcode: str = Query(None),
):
    from_parsed = parse_datetime(from_dt) if from_dt else datetime.now() - timedelta(days=1)
    to_parsed = parse_datetime(to_dt) if to_dt else datetime.now()

    service = CarbonIntensityService()
    response = service.get_intensity_between(from_parsed, to_parsed)
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    return _flatten_intensity_list(response)


@router.get("/carbon-intensity/latest/")
def latest_carbon_intensity():
    service = CarbonIntensityService()
    response = service.get_current_intensity()
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    entries = _flatten_intensity_list(response)
    if not entries:
        raise HTTPException(status_code=404, detail="No data available")
    return entries[-1]


@router.get("/carbon-intensity/current/")
def current_carbon_intensity():
    service = CarbonIntensityService()
    response = service.get_current_intensity()
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    return _flatten_intensity_list(response)


@router.get("/carbon-intensity/regional/")
def regional_carbon_intensity():
    service = CarbonIntensityService()
    response = service.get_regional_current()
    return response


@router.get("/carbon-intensity/today/")
def today_carbon_intensity():
    service = CarbonIntensityService()
    response = service.get_intensity_today()
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    return _flatten_intensity_list(response)


@router.get("/carbon-intensity/date/{date}/")
def carbon_intensity_by_date(date: str):
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    service = CarbonIntensityService()
    response = service.get_intensity_date(parsed_date)
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    return _flatten_intensity_list(response)


@router.get("/carbon-intensity/quarterly-generationmix/")
def quarterly_generation_mix(
    year: int = Query(None),
    quarter: int = Query(None),
):
    if not year or not quarter:
        raise HTTPException(
            status_code=400, detail="Year and quarter are required parameters."
        )

    file_path = os.path.join(
        os.path.dirname(__file__),
        "../data/generationmix/monthly_generation_averages.json",
    )
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Data file not found.")

    with open(file_path, "r") as f:
        data = json.load(f)

    filtered_data = {}
    for month, regions in data.items():
        month_date = datetime.strptime(month, "%Y-%m")
        if month_date.year == year and (month_date.month - 1) // 3 + 1 == quarter:
            filtered_data[month] = regions

    return filtered_data


@router.get("/carbon-intensity/stats/{from_time}/{to_time}/")
def carbon_intensity_stats(from_time: str, to_time: str):
    from_parsed = parse_datetime(from_time)
    to_parsed = parse_datetime(to_time)
    service = CarbonIntensityService()
    response = service.get_statistics(from_parsed, to_parsed)
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    return _flatten_stats(response, from_time, to_time)


@router.get("/generation-mix/")
def list_generation_mix(
    from_dt: str = Query(None, alias="from"),
    to_dt: str = Query(None, alias="to"),
):
    service = CarbonIntensityService()
    if from_dt and to_dt:
        response = service.get_generation_range(parse_datetime(from_dt), parse_datetime(to_dt))
    else:
        response = service.get_current_generation()
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    data = response["data"]
    if isinstance(data, list):
        return [_flatten_generation_mix_entry(entry) for entry in data]
    return [_flatten_generation_mix_entry(data)]


@router.get("/generation-mix/latest/")
def latest_generation_mix():
    service = CarbonIntensityService()
    response = service.get_current_generation()
    if not response or "data" not in response:
        raise HTTPException(status_code=404, detail="No data available")
    data = response["data"]
    if isinstance(data, list):
        return _flatten_generation_mix_entry(data[-1]) if data else None
    return _flatten_generation_mix_entry(data)
