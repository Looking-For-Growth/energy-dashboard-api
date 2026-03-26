from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GridSupplyPointSchema(BaseModel):
    group_id: str


class GSPPriceSchema(BaseModel):
    value_exc_vat: float
    value_inc_vat: float
    valid_from: datetime
    valid_to: Optional[datetime] = None
