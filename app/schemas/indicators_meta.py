from pydantic import BaseModel
from typing import Optional, List

class IndicatorMetaBase(BaseModel):
    code: str
    name: str
    topic_id: int
    source_note: Optional[str]

class IndicatorMetaCreate(IndicatorMetaBase):
    pass

class IndicatorMetaUpdate(BaseModel):
    name: Optional[str]
    topic_id: Optional[int]
    source_note: Optional[str]

class IndicatorMetaOut(IndicatorMetaBase):
    id: int

    class Config:
        from_attributes = True
