from pydantic import BaseModel
from typing import List

class ConstituentModel(BaseModel):
    name: str
    weight: float
    latest_price: float

class PriceDateModel(BaseModel):
    date: str
    price: float

class TopHoldingModel(BaseModel):
    name: str
    weight: float
    latest_price: float
    holding_value: float

class ETFResponse(BaseModel):
    id: str
    name: str
    constituent_count: int
