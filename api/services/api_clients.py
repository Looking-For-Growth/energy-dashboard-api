from datetime import datetime
import logging
import requests
from typing import Dict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

import config
from services.base_client import (
    BaseService,
    ExternalAPIError,
    RateLimitError,
    NetworkError,
    ServiceUnavailableError,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class CarbonIntensityService(BaseService):
    def __init__(self, base_url="https://api.carbonintensity.org.uk/"):
        super().__init__(base_url)

    # Carbon Intensity - National endpoints
    def get_current_intensity(self):
        """Gets current carbon intensity."""
        return self._get("intensity")

    def get_intensity_today(self):
        """Gets carbon intensity for today."""
        return self._get("intensity/date")

    def get_intensity_date(self, date):
        """Gets carbon intensity for specified date."""
        return self._get(f"intensity/date/{date.isoformat()}")

    def get_intensity_date_period(self, date, period):
        """Gets carbon intensity for specified date and settlement period."""
        return self._get(f"intensity/date/{date.isoformat()}/{period}")

    def get_intensity_factors(self):
        """Gets carbon intensity factors for fuel types."""
        return self._get("intensity/factors")

    def get_intensity_from(self, from_time):
        """Gets carbon intensity for specified date."""
        return self._get(f"intensity/{from_time.isoformat()}")

    def get_intensity_fw24h(self, from_time):
        """Gets carbon intensity for 24h after specified date."""
        return self._get(f"intensity/{from_time.isoformat()}/fw24h")

    def get_intensity_fw48h(self, from_time):
        """Gets carbon intensity for 48h after specified date."""
        return self._get(f"intensity/{from_time.isoformat()}/fw48h")

    def get_intensity_pt24h(self, from_time):
        """Gets carbon intensity for 24h before specified date."""
        return self._get(f"intensity/{from_time.isoformat()}/pt24h")

    def get_intensity_between(self, from_time, to_time):
        """Gets carbon intensity between specified datetimes"""
        return self._get(f"intensity/{from_time.isoformat()}/{to_time.isoformat()}")

    # Statistics - National endpoints
    def get_statistics(self, from_time, to_time):
        """Gets carbon intensity statistics between specified datetimes."""
        return self._get(
            f"intensity/stats/{from_time.isoformat()}/{to_time.isoformat()}"
        )

    def get_statistics_block(self, from_time, to_time, block):
        """Gets carbon intensity statistics in blocks between specified datetimes."""
        return self._get(
            f"intensity/stats/{from_time.isoformat()}/{to_time.isoformat()}/{block}"
        )

    # Generation Mix - National (beta) endpoints
    def get_current_generation(self):
        """Gets current generation mix."""
        return self._get("generation")

    def get_generation_pt24h(self, from_time):
        """Gets generation mix for 24h before specified date."""
        return self._get(f"generation/{from_time.isoformat()}/pt24h")

    def get_generation_range(self, from_time, to_time):
        """Gets generation mix between specified datetimes."""
        return self._get(f"generation/{from_time.isoformat()}/{to_time.isoformat()}")

    # Carbon Intensity - Regional (beta) endpoints
    def get_regional_current(self):
        """Gets current carbon intensity for GB regions."""
        return self._get("regional")

    def get_regional_england(self):
        """Gets current carbon intensity for England."""
        return self._get("regional/england")

    def get_regional_scotland(self):
        """Gets current carbon intensity for Scotland."""
        return self._get("regional/scotland")

    def get_regional_wales(self):
        """Gets current carbon intensity for Wales."""
        return self._get("regional/wales")

    def get_regional_postcode(self, postcode):
        """Gets current carbon intensity for specified outward postcode."""
        return self._get(f"regional/postcode/{postcode}")

    def get_regional_regionid(self, regionid):
        """Gets current carbon intensity for specified region."""
        return self._get(f"regional/regionid/{regionid}")

    def get_regional_intensity_fw24h(self, from_time):
        """Gets carbon intensity for 24h after specified datetime for GB regions."""
        return self._get(f"regional/intensity/{from_time.isoformat()}/fw24h")

    def get_regional_intensity_fw24h_postcode(self, from_time, postcode):
        """Gets carbon intensity for 24h after specified datetime for specified outward postcode."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/fw24h/postcode/{postcode}"
        )

    def get_regional_intensity_fw24h_regionid(self, from_time, regionid):
        """Gets carbon intensity for 24h after specified datetime for specified region."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/fw24h/regionid/{regionid}"
        )

    def get_regional_intensity_fw48h(self, from_time):
        """Gets carbon intensity for 48h after specified datetime for GB regions."""
        return self._get(f"regional/intensity/{from_time.isoformat()}/fw48h")

    def get_regional_intensity_fw48h_postcode(self, from_time, postcode):
        """Gets carbon intensity for 48h after specified datetime for specified outward postcode."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/fw48h/postcode/{postcode}"
        )

    def get_regional_intensity_fw48h_regionid(self, from_time, regionid):
        """Gets carbon intensity for 48h after specified datetime for specified region."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/fw48h/regionid/{regionid}"
        )

    def get_regional_intensity_pt24h(self, from_time):
        """Gets carbon intensity for 24h before specified datetime for GB regions."""
        return self._get(f"regional/intensity/{from_time.isoformat()}/pt24h")

    def get_regional_intensity_pt24h_postcode(self, from_time, postcode):
        """Gets carbon intensity for 24h before specified datetime for specified outward postcode."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/pt24h/postcode/{postcode}"
        )

    def get_regional_intensity_pt24h_regionid(self, from_time, regionid):
        """Gets carbon intensity for 24h before specified datetime for specified region."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/pt24h/regionid/{regionid}"
        )

    def get_regional_intensity_range(self, from_time, to_time):
        """Gets carbon intensity between specified datetimes for GB regions."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/{to_time.isoformat()}"
        )

    def get_regional_intensity_range_postcode(self, from_time, to_time, postcode):
        """Gets carbon intensity between specified datetimes for specified outward postcode."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/{to_time.isoformat()}/postcode/{postcode}"
        )

    def get_regional_intensity_range_regionid(self, from_time, to_time, regionid):
        """Gets carbon intensity between specified datetimes for specified region."""
        return self._get(
            f"regional/intensity/{from_time.isoformat()}/{to_time.isoformat()}/regionid/{regionid}"
        )


class BMRSService(BaseService):
    class BMRSAPIError(ExternalAPIError):
        """BMRS-specific errors"""

    class BMRSRateLimitError(RateLimitError):
        """BMRS-specific rate limiting error"""

    def __init__(self, api_key: str = config.BMRS_API_KEY):
        super().__init__(
            base_url="https://data.elexon.co.uk/bmrs/api/v1", logger_name="BMRS Service"
        )
        if not api_key:
            raise ValueError("BMRS API key is required")
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        return {**super()._get_headers(), "Authorization": f"Bearer {self.api_key}"}

    def _handle_error_response(self, response: requests.Response):
        """BMRS-specific error handling"""
        if "quota exceeded" in response.text.lower():
            raise self.BMRSRateLimitError("BMRS API quota exceeded")

        super()._handle_error_response(response)

    def _get_retry_policy(self):
        """BMRS-specific retry policy"""
        return retry(
            stop=stop_after_attempt(5),  # More retries for BMRS
            wait=wait_exponential(multiplier=2, min=1, max=30),
            retry=(
                retry_if_exception_type((NetworkError, ServiceUnavailableError))
                | retry_if_exception_type(self.BMRSRateLimitError)
            ),
        )

    # Balancing Mechanism Dynamic Endpoints

    def get_balancing_dynamic(
        self,
        bmUnit,
        snapshotAt,
        until=None,
        snapshotAtSettlementPeriod=None,
        untilSettlementPeriod=None,
        dataset=None,
        format="json",
    ):
        params = {
            "bmUnit": bmUnit,
            "snapshotAt": snapshotAt,
            "until": until,
            "snapshotAtSettlementPeriod": snapshotAtSettlementPeriod,
            "untilSettlementPeriod": untilSettlementPeriod,
            "dataset": dataset,
            "format": format,
        }

        return self._get("/balancing/dynamic", params=params)

    def get_balancing_dynamic_all(
        self, settlementDate, settlementPeriod, bmUnit=None, dataset=None, format="json"
    ):
        params = {
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "bmUnit": bmUnit,
            "dataset": dataset,
            "format": format,
        }

        return self._get("/balancing/dynamic/all", params=params)

    def get_balancing_dynamic_rates(
        self,
        bmUnit,
        snapshotAt,
        until=None,
        snapshotAtSettlementPeriod=None,
        untilSettlementPeriod=None,
        dataset=None,
        format="json",
    ):
        params = {
            "bmUnit": bmUnit,
            "snapshotAt": snapshotAt,
            "until": until,
            "snapshotAtSettlementPeriod": snapshotAtSettlementPeriod,
            "untilSettlementPeriod": untilSettlementPeriod,
            "dataset": dataset,
            "format": format,
        }

        return self._get("/balancing/dynamic/rates", params=params)

    def get_balancing_dynamic_rates_all(
        self, settlementDate, settlementPeriod, bmUnit=None, dataset=None, format="json"
    ):
        params = {
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "bmUnit": bmUnit,
            "dataset": dataset,
            "format": format,
        }

        return self._get("/balancing/dynamic/rates/all", params=params)

    # Balancing Mechanism Physical Endpoints

    def get_balancing_physical(
        self,
        bmUnit,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        dataset=None,
        format="json",
    ):
        params = {
            "bmUnit": bmUnit,
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "dataset": dataset,
            "format": format,
        }

        return self._get("/balancing/physical", params=params)

    def get_balancing_physical_all(
        self, dataset, settlementDate, settlementPeriod, bmUnit=None, format="json"
    ):
        params = {
            "dataset": dataset,
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/balancing/physical/all", params=params)

    # Balancing Services Adjustment - Disaggregated Endpoints

    def get_balancing_nonbm_disbsad_summary(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "format": format,
        }

        return self._get("/balancing/nonbm/disbsad/summary", params=params)

    def get_balancing_nonbm_disbsad_details(
        self, settlementDate, settlementPeriod, format="json"
    ):
        params = {
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "format": format,
        }
        return self._get("/balancing/nonbm/disbsad/details", params=params)

    # Balancing Services Adjustment - Net Endpoints

    def get_balancing_nonbm_netbsad(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        includeZero=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "includeZero": includeZero,
            "format": format,
        }

        return self._get("/balancing/nonbm/netbsad", params=params)

    def get_balancing_nonbm_netbsad_events(
        self, count, before=None, settlementPeriodBefore=None, format="json"
    ):
        params = {
            "count": count,
            "before": before,
            "settlementPeriodBefore": settlementPeriodBefore,
            "format": format,
        }

        return self._get("/balancing/nonbm/netbsad/events", params=params)

    # Bid-Offer Endpoints

    def get_balancing_bid_offer(
        self,
        bmUnit,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        format="json",
    ):
        params = {
            "bmUnit": bmUnit,
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "format": format,
        }

        return self._get("/balancing/bid-offer", params=params)

    def get_balancing_bid_offer_all(
        self, settlementDate, settlementPeriod, bmUnit=None, format="json"
    ):
        params = {
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/balancing/bid-offer/all", params=params)

    # Bid-Offer Acceptances Endpoints

    def get_balancing_acceptances(
        self,
        bmUnit,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        format="json",
    ):
        params = {
            "bmUnit": bmUnit,
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "format": format,
        }

        return self._get("/balancing/acceptances", params=params)

    def get_balancing_acceptances_all(
        self, settlementDate, settlementPeriod, bmUnit=None, format="json"
    ):
        params = {
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/balancing/acceptances/all", params=params)

    def get_balancing_acceptances_all_latest(self, format="json"):
        params = {"format": format}
        return self._get("/balancing/acceptances/all/latest", params=params)

    def get_balancing_acceptances_by_id(self, acceptanceNumber, format="json"):
        params = {"format": format}
        return self._get("/balancing/acceptances/{acceptanceNumber}", params=params)

    # BMRS Datasets Endpoints

    def get_datasets_nonbm(self, from_date=None, to=None, format="json"):
        params = {"from": from_date, "to": to, "format": format}

        return self._get("/datasets/NONBM", params=params)

    def get_datasets_nonbm_stream(self, from_date=None, to=None):
        params = {"from": from_date, "to": to}

        return self._get("/datasets/NONBM/stream", params=params)

    def get_datasets_pn(
        self, settlementDate, settlementPeriod, bmUnit=None, format="json"
    ):
        params = {
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/datasets/PN", params=params)

    def get_datasets_pn_stream(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
        }

        return self._get("/datasets/PN/stream", params=params)

    def get_datasets_qpn(
        self, settlementDate, settlementPeriod, bmUnit=None, format="json"
    ):
        params = {
            "settlementDate": settlementDate,
            "settlementPeriod": settlementPeriod,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/datasets/QPN", params=params)

    def get_datasets_qpn_stream(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
        }

        return self._get("/datasets/QPN/stream", params=params)

    def get_datasets_mels(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/datasets/MELS", params=params)

    def get_datasets_mels_stream(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
        }

        return self._get("/datasets/MELS/stream", params=params)

    def get_datasets_mils(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/datasets/MILS", params=params)

    def get_datasets_mils_stream(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
        }

        return self._get("/datasets/MILS/stream", params=params)

    def get_datasets_qas(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/datasets/QAS", params=params)

    def get_datasets_qas_stream(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
        }

        return self._get("/datasets/QAS/stream", params=params)

    def get_datasets_netbsad(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "format": format,
        }

        return self._get("/datasets/NETBSAD", params=params)

    def get_datasets_netbsad_stream(
        self, from_date, to_date, settlementPeriodFrom=None, settlementPeriodTo=None
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
        }

        return self._get("/datasets/NETBSAD/stream", params=params)

    def get_datasets_disbsad(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "format": format,
        }

        return self._get("/datasets/DISBSAD", params=params)

    def get_datasets_disbsad_stream(
        self, from_date, to_date, settlementPeriodFrom=None, settlementPeriodTo=None
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
        }

        return self._get("/datasets/DISBSAD/stream", params=params)

    def get_datasets_bod(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/datasets/BOD", params=params)

    def get_datasets_bod_stream(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
        }

        return self._get("/datasets/BOD/stream", params=params)

    def get_datasets_boalf(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
            "format": format,
        }

        return self._get("/datasets/BOALF", params=params)

    def get_datasets_boalf_stream(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        bmUnit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "bmUnit": bmUnit,
        }

        return self._get("/datasets/BOALF/stream", params=params)

    def get_datasets_mid(
        self,
        from_date,
        to_date,
        settlementPeriodFrom=None,
        settlementPeriodTo=None,
        dataProviders=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlementPeriodFrom,
            "settlementPeriodTo": settlementPeriodTo,
            "dataProviders": dataProviders,
            "format": format,
        }

        return self._get("/datasets/MID", params=params)

    # MID Stream
    def get_datasets_mid_stream(
        self,
        from_date,
        to_date,
        settlement_period_from=None,
        settlement_period_to=None,
        data_providers=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlement_period_from,
            "settlementPeriodTo": settlement_period_to,
            "dataProviders": data_providers,
        }
        return self._get("/datasets/MID/stream", params=params)

    # FUELHH
    def get_datasets_fuelhh(
        self,
        publish_date_time_from=None,
        publish_date_time_to=None,
        settlement_date_from=None,
        settlement_date_to=None,
        settlement_period=None,
        fuel_type=None,
        format="json",
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "settlementDateFrom": settlement_date_from,
            "settlementDateTo": settlement_date_to,
            "settlementPeriod": settlement_period,
            "fuelType": fuel_type,
            "format": format,
        }
        return self._get("/datasets/FUELHH", params=params)

    # FUELHH Stream
    def get_datasets_fuelhh_stream(
        self,
        publish_date_time_from=None,
        publish_date_time_to=None,
        settlement_date_from=None,
        settlement_date_to=None,
        settlement_period=None,
        fuel_type=None,
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "settlementDateFrom": settlement_date_from,
            "settlementDateTo": settlement_date_to,
            "settlementPeriod": settlement_period,
            "fuelType": fuel_type,
        }
        return self._get("/datasets/FUELHH/stream", params=params)

    # FUELINST
    def get_datasets_fuelinst(
        self,
        publish_date_time_from=None,
        publish_date_time_to=None,
        settlement_date_from=None,
        settlement_date_to=None,
        settlement_period=None,
        fuel_type=None,
        format="json",
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "settlementDateFrom": settlement_date_from,
            "settlementDateTo": settlement_date_to,
            "settlementPeriod": settlement_period,
            "fuelType": fuel_type,
            "format": format,
        }
        return self._get("/datasets/FUELINST", params=params)

    # FUELINST Stream
    def get_datasets_fuelinst_stream(
        self,
        publish_date_time_from=None,
        publish_date_time_to=None,
        settlement_date_from=None,
        settlement_date_to=None,
        settlement_period=None,
        fuel_type=None,
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "settlementDateFrom": settlement_date_from,
            "settlementDateTo": settlement_date_to,
            "settlementPeriod": settlement_period,
            "fuelType": fuel_type,
        }
        return self._get("/datasets/FUELINST/stream", params=params)

    # UOU2T14D
    def get_datasets_uou2t14d(
        self,
        fuel_type=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        bm_unit=None,
        format="json",
    ):
        params = {
            "fuelType": fuel_type,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "bmUnit": bm_unit,
            "format": format,
        }
        return self._get("/datasets/UOU2T14D", params=params)

    # UOU2T14D Stream
    def get_datasets_uou2t14d_stream(
        self,
        fuel_type=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        bm_unit=None,
    ):
        params = {
            "fuelType": fuel_type,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "bmUnit": bm_unit,
        }
        return self._get("/datasets/UOU2T14D/stream", params=params)

    # UOU2T3YW
    def get_datasets_uou2t3yw(
        self,
        fuel_type=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        bm_unit=None,
        format="json",
    ):
        params = {
            "fuelType": fuel_type,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "bmUnit": bm_unit,
            "format": format,
        }
        return self._get("/datasets/UOU2T3YW", params=params)

    # UOU2T3YW Stream
    def get_datasets_uou2t3yw_stream(
        self,
        fuel_type=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        bm_unit=None,
    ):
        params = {
            "fuelType": fuel_type,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "bmUnit": bm_unit,
        }
        return self._get("/datasets/UOU2T3YW/stream", params=params)

    # FOU2T14D
    def get_datasets_fou2t14d(
        self,
        fuel_type=None,
        publish_date=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        bidding_zone=None,
        interconnector=None,
        format="json",
    ):
        params = {
            "fuelType": fuel_type,
            "publishDate": publish_date,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "biddingZone": bidding_zone,
            "interconnector": interconnector,
            "format": format,
        }
        return self._get("/datasets/FOU2T14D", params=params)

    # FOU2T3YW
    def get_datasets_fou2t3yw(
        self,
        fuel_type=None,
        publish_date=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        week=None,
        year=None,
        bidding_zone=None,
        interconnector=None,
        format="json",
    ):
        params = {
            "fuelType": fuel_type,
            "publishDate": publish_date,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "week": week,
            "year": year,
            "biddingZone": bidding_zone,
            "interconnector": interconnector,
            "format": format,
        }
        return self._get("/datasets/FOU2T3YW", params=params)

    # NOU2T14D
    def get_datasets_nou2t14d(
        self,
        publish_date=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        format="json",
    ):
        params = {
            "publishDate": publish_date,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/NOU2T14D", params=params)

    # NOU2T3YW
    def get_datasets_nou2t3yw(
        self,
        publish_date=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        week=None,
        year=None,
        format="json",
    ):
        params = {
            "publishDate": publish_date,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "week": week,
            "year": year,
            "format": format,
        }
        return self._get("/datasets/NOU2T3YW", params=params)

    # TEMP
    def get_datasets_temp(
        self, publish_date_time_from=None, publish_date_time_to=None, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/TEMP", params=params)

    # INDGEN
    def get_datasets_indgen(
        self,
        boundary=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        format="json",
    ):
        params = {
            "boundary": boundary,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/INDGEN", params=params)

    # INDGEN Stream
    def get_datasets_indgen_stream(
        self, boundary=None, publish_date_time_from=None, publish_date_time_to=None
    ):
        params = {
            "boundary": boundary,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/INDGEN/stream", params=params)

    # INDDEM
    def get_datasets_inddem(
        self,
        boundary=None,
        publish_date_time_from=None,
        publish_date_time_to=None,
        format="json",
    ):
        params = {
            "boundary": boundary,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/INDDEM", params=params)

    # INDDEM Stream
    def get_datasets_inddem_stream(
        self, boundary=None, publish_date_time_from=None, publish_date_time_to=None
    ):
        params = {
            "boundary": boundary,
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/INDDEM/stream", params=params)

    # SYSWARN
    def get_datasets_syswarn(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/SYSWARN", params=params)

    # SYSWARN Stream
    def get_datasets_syswarn_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/SYSWARN/stream", params=params)

    # DCI Endpoints
    def get_datasets_dci(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/DCI", params=params)

    def get_datasets_dci_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/DCI/stream", params=params)

    # SOSO Endpoints
    def get_datasets_soso(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/SOSO", params=params)

    def get_datasets_soso_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/SOSO/stream", params=params)

    # TUDM Endpoints
    def get_datasets_tudm(
        self,
        settlement_date,
        settlement_period,
        trading_unit_name=None,
        trading_unit_type=None,
        format="json",
    ):
        params = {
            "settlementDate": settlement_date,
            "settlementPeriod": settlement_period,
            "tradingUnitName": trading_unit_name,
            "tradingUnitType": trading_unit_type,
            "format": format,
        }
        return self._get("/datasets/TUDM", params=params)

    def get_datasets_tudm_stream(
        self,
        settlement_date_from,
        settlement_period_from,
        settlement_date_to,
        settlement_period_to,
        trading_unit_name=None,
        trading_unit_type=None,
    ):
        params = {
            "settlementDateFrom": settlement_date_from,
            "settlementPeriodFrom": settlement_period_from,
            "settlementDateTo": settlement_date_to,
            "settlementPeriodTo": settlement_period_to,
            "tradingUnitName": trading_unit_name,
            "tradingUnitType": trading_unit_type,
        }
        return self._get("/datasets/TUDM/stream", params=params)

    # SIL Endpoints
    def get_datasets_sil(self, from_date, to_date, bm_unit=None, format="json"):
        params = {"from": from_date, "to": to_date, "bmUnit": bm_unit, "format": format}
        return self._get("/datasets/SIL", params=params)

    def get_datasets_sil_stream(self, from_date, to_date, bm_unit=None):
        params = {"from": from_date, "to": to_date, "bmUnit": bm_unit}
        return self._get("/datasets/SIL/stream", params=params)

    # MZT Endpoints
    def get_datasets_mzt(
        self,
        from_date,
        to_date,
        settlement_period_from=None,
        settlement_period_to=None,
        bm_unit=None,
        format="json",
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlement_period_from,
            "settlementPeriodTo": settlement_period_to,
            "bmUnit": bm_unit,
            "format": format,
        }
        return self._get("/datasets/MZT", params=params)

    def get_datasets_mzt_stream(
        self,
        from_date,
        to_date,
        settlement_period_from=None,
        settlement_period_to=None,
        bm_unit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlement_period_from,
            "settlementPeriodTo": settlement_period_to,
            "bmUnit": bm_unit,
        }
        return self._get("/datasets/MZT/stream", params=params)

    # Example for AGWS:
    def get_datasets_agws(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/AGWS", params=params)

    def get_datasets_agws_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/AGWS/stream", params=params)

    # B1610 Endpoints
    def get_datasets_b1610(
        self, settlement_date, settlement_period, bm_unit=None, format="json"
    ):
        params = {
            "settlementDate": settlement_date,
            "settlementPeriod": settlement_period,
            "bmUnit": bm_unit,
            "format": format,
        }
        return self._get("/datasets/B1610", params=params)

    def get_datasets_b1610_stream(
        self,
        from_date,
        to_date,
        settlement_period_from=None,
        settlement_period_to=None,
        bm_unit=None,
    ):
        params = {
            "from": from_date,
            "to": to_date,
            "settlementPeriodFrom": settlement_period_from,
            "settlementPeriodTo": settlement_period_to,
            "bmUnit": bm_unit,
        }
        return self._get("/datasets/B1610/stream", params=params)

    # REMIT Endpoints
    def get_datasets_remit(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/REMIT", params=params)

    def get_datasets_remit_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/REMIT/stream", params=params)

    # WATL Endpoints
    def get_datasets_watl(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/WATL", params=params)

    def get_datasets_watl_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/WATL/stream", params=params)

    # New dataset endpoints
    def get_datasets_dag(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/DAG", params=params)

    def get_datasets_dag_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/DAG/stream", params=params)

    def get_datasets_matl(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/MATL", params=params)

    def get_datasets_matl_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/MATL/stream", params=params)

    def get_datasets_yatl(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/YATL", params=params)

    def get_datasets_yatl_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/YATL/stream", params=params)

    def get_datasets_ccm(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/CCM", params=params)

    def get_datasets_ccm_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/CCM/stream", params=params)

    def get_datasets_yafm(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/YAFM", params=params)

    def get_datasets_yafm_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/YAFM/stream", params=params)

    def get_datasets_abuc(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/ABUC", params=params)

    def get_datasets_abuc_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/ABUC/stream", params=params)

    def get_datasets_ppbr(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/PPBR", params=params)

    def get_datasets_ppbr_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/PPBR/stream", params=params)

    def get_datasets_feib(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/FEIB", params=params)

    def get_datasets_feib_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/FEIB/stream", params=params)

    def get_datasets_aobe(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/AOBE", params=params)

    def get_datasets_aobe_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/AOBE/stream", params=params)

    def get_datasets_beb(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/BEB", params=params)

    def get_datasets_beb_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/BEB/stream", params=params)

    def get_datasets_cbs(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/CBS", params=params)

    def get_datasets_cbs_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/CBS/stream", params=params)

    def get_datasets_pbc(
        self, publish_date_time_from, publish_date_time_to, format="json"
    ):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
            "format": format,
        }
        return self._get("/datasets/PBC", params=params)

    def get_datasets_pbc_stream(self, publish_date_time_from, publish_date_time_to):
        params = {
            "publishDateTimeFrom": publish_date_time_from,
            "publishDateTimeTo": publish_date_time_to,
        }
        return self._get("/datasets/PBC/stream", params=params)

    def get_cdn(self, format="json"):
        params = {"format": format}
        return self._get("/CDN", params=params)

    #####################################################################################
    # Demand Endpoints
    #####################################################################################

    def get_demand_outturn(
        self,
        settlement_date_from,
        settlement_date_to,
        settlement_period=None,
        format="json",
    ):
        params = {
            "settlementDateFrom": settlement_date_from,
            "settlementDateTo": settlement_date_to,
            "settlementPeriod": settlement_period,
            "format": format,
        }
        return self._get("/demand/outturn", params=params)


class OctopusService(BaseService):
    def __init__(self):
        super().__init__(base_url="https://api.octopus.energy/v1/")

    def get_grid_supply_points(self, format="json"):
        params = {
            "format": format,
        }
        return self._get("industry/grid-supply-points", params=params)

    def get_grid_supply_point_by_postcode(self, format="json", postcode="SW1A1AA"):
        params = {
            "format": format,
            "postcode": postcode,
        }
        response = self._get("industry/grid-supply-points", params=params)

        return response["results"][0]["group_id"].replace("_", "")  # "C"

    def get_gsp_price(self, gsp, from_date, to_date, format="json"):
        """TODO: Fix for 2025 data that always returns null - unsure if this is an Octopus issue"""
        params = {
            "format": format,
        }
        return self._get(
            f"products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-{gsp}/standard-unit-rates/?period_from={from_date.isoformat()}Z&period_to={to_date.isoformat()}Z",
            params=params,
        )

    def get_gsp_price_today(self, gsp, format="json"):
        params = {
            "format": format,
        }
        print(
            "Date:",
            datetime.today()
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .isoformat(),
            "date2:",
            datetime.now().replace(second=0, microsecond=0).isoformat(),
        )
        return self._get(
            f"products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-{gsp}/standard-unit-rates/?period_from={datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()}Z&period_to={datetime.now().replace(second=0, microsecond=0).isoformat()}Z",
            params=params,
        )
