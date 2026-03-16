from fastapi import APIRouter, UploadFile, File
from typing import List
from ..models import ETFResponse, ConstituentModel, PriceDateModel, TopHoldingModel
from ..services import etf_service

router = APIRouter(prefix="/api/etfs", tags=["etfs"])

@router.post("/upload", response_model=ETFResponse, status_code=201)
async def upload_etf(file: UploadFile = File(...)):
    content = await file.read()
    name = file.filename.rsplit('.', 1)[0] if file.filename else "Unknown_ETF"
    return etf_service.process_etf_upload(name, content)

@router.get("/{id}/constituents", response_model=List[ConstituentModel])
def get_constituents(id: int):
    return etf_service.get_etf_constituents(id)

@router.get("/{id}/price-history", response_model=List[PriceDateModel])
def get_price_history(id: int):
    return etf_service.get_etf_price_history(id)

@router.get("/{id}/top-holdings", response_model=List[TopHoldingModel])
def get_top_holdings(id: int):
    return etf_service.get_etf_top_holdings(id)
