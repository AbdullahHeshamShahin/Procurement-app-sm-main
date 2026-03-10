"""Request-related models."""
from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RequestStatus(str, Enum):
    """Request status enumeration."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


class OrderLine(BaseModel):
    """Order line item model."""
    description: str = Field(..., min_length=1, description="Description is required")
    unit_price: float = Field(..., gt=0, description="Unit price must be greater than 0")
    amount: float = Field(
        ..., gt=0, description="Amount must be greater than 0"
    )  # Supports decimal quantities (e.g., 1.28 qm, 4.80 Lfm)
    unit: str = Field(..., min_length=1, description="Unit is required")
    total_price: float = Field(..., ge=0, description="Total price for this line")


class StatusHistoryEntry(BaseModel):
    """Status history entry model."""
    status: RequestStatus
    changed_at: datetime
    changed_by: Optional[str] = None
    notes: Optional[str] = None


class ProcurementRequest(BaseModel):
    """Full procurement request model."""
    requestor_name: str
    title: str
    vendor_name: str
    vat_id: str
    commodity_group_id: str
    commodity_group_name: Optional[str] = None
    order_lines: List[OrderLine]
    total_cost: float
    department: str
    status: RequestStatus = RequestStatus.OPEN
    status_history: List[StatusHistoryEntry] = []
    archived: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProcurementRequestCreate(BaseModel):
    """Model for creating a new procurement request. All fields marked with * in the UI are required."""

    requestor_name: str = Field(..., min_length=1, description="Requestor name is required")
    title: str = Field(..., min_length=1, description="Title is required")
    vendor_name: str = Field(..., min_length=1, description="Vendor name is required")
    vat_id: str = Field(..., min_length=1, description="VAT ID is required")
    commodity_group_id: str = Field(..., min_length=1, description="Commodity group is required")
    order_lines: List[OrderLine] = Field(..., min_length=1, description="At least one order line is required")
    total_cost: float = Field(..., gt=0, description="Total cost must be greater than 0")
    department: str = Field(..., min_length=1, description="Department is required")


class ProcurementRequestUpdate(BaseModel):
    """Model for updating a procurement request."""
    requestor_name: Optional[str] = None
    title: Optional[str] = None
    vendor_name: Optional[str] = None
    vat_id: Optional[str] = None
    commodity_group_id: Optional[str] = None
    order_lines: Optional[List[OrderLine]] = None
    total_cost: Optional[float] = None
    department: Optional[str] = None


class StatusUpdate(BaseModel):
    """Model for updating request status."""
    status: RequestStatus
    changed_by: Optional[str] = None
    notes: Optional[str] = None


class ProcurementRequestResponse(BaseModel):
    """Response model for procurement request."""
    id: str
    requestor_name: str
    title: str
    vendor_name: str
    vat_id: str
    commodity_group_id: str
    commodity_group_name: str
    order_lines: List[OrderLine]
    total_cost: float
    department: str
    status: RequestStatus
    status_history: List[StatusHistoryEntry]
    archived: bool = False
    created_at: datetime
    updated_at: datetime

