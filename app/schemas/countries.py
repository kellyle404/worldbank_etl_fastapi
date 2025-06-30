from pydantic import BaseModel
from typing import Optional

class CountryBase(BaseModel):
    name: str
    iso3: Optional[str]
    region: Optional[str]

class CountryCreate(CountryBase):
    pass

class CountryUpdate(BaseModel):
    name: Optional[str]
    iso3: Optional[str]
    region: Optional[str]

class CountryOut(CountryBase):
    id: int

    class Config:
        from_attributes = True