from pydantic import BaseModel
from typing import Optional

class IndicatorValueBase(BaseModel):
    indicator_id: int
    country_id: int
    date: int
    value: float

class IndicatorValueCreate(IndicatorValueBase):
    pass

class IndicatorValueUpdate(BaseModel):
    value: Optional[float]

class IndicatorValueOut(IndicatorValueBase):
    id: int

    class Config:
        from_attributes = True
