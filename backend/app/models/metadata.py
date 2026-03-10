"""Metadata and AI-related models."""
from typing import List, Optional
from pydantic import BaseModel
from app.models.request import OrderLine


class CommodityGroup(BaseModel):
    """Commodity group model."""
    id: str
    category: str
    name: str


class DocumentExtractionResponse(BaseModel):
    """Response model for document extraction."""
    requestor_name: Optional[str] = None
    title: Optional[str] = None
    vendor_name: Optional[str] = None
    vat_id: Optional[str] = None
    department: Optional[str] = None
    order_lines: List[OrderLine] = []
    total_cost: Optional[float] = None
    suggested_commodity_group_id: Optional[str] = None
    suggested_commodity_group_name: Optional[str] = None
    extraction_confidence: float = 0.0


class CommodityGroupSuggestion(BaseModel):
    """Commodity group suggestion model."""
    commodity_group_id: str
    commodity_group_name: str
    category: str
    confidence: float
    reasoning: str


class TextExtractionResponse(BaseModel):
    """Response model for raw text extraction from documents."""
    text: str
    file_name: str
    file_type: str

