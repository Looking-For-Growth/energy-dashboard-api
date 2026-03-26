from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CarbonIntensitySchema(BaseModel):
    from_datetime: datetime
    to_datetime: datetime
    actual: Optional[int] = None
    forecast: Optional[int] = None
    index: str


class CarbonIntensityStatsSchema(BaseModel):
    from_datetime: datetime
    to_datetime: datetime
    min_intensity: int
    max_intensity: int
    average_intensity: float
