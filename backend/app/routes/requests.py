"""Routes for procurement request management."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.models.request import (
    ProcurementRequestCreate,
    ProcurementRequestUpdate,
    ProcurementRequestResponse,
    StatusUpdate,
    RequestStatus,
    StatusHistoryEntry,
)
from app.services.request_service import RequestService

router = APIRouter()
request_service = RequestService()


@router.post("/requests", response_model=ProcurementRequestResponse)
async def create_request(request: ProcurementRequestCreate):
    """Create a new procurement request."""
    return await request_service.create_request(request)


@router.get("/requests", response_model=List[ProcurementRequestResponse])
async def get_requests(
    status: Optional[RequestStatus] = None,
    department: Optional[str] = None,
    archived: Optional[bool] = None,
):
    """Get all procurement requests with optional filtering."""
    return await request_service.get_requests(
        status=status, department=department, archived=archived
    )


@router.get("/requests/{request_id}", response_model=ProcurementRequestResponse)
async def get_request(request_id: str):
    """Get a specific procurement request by ID."""
    return await request_service.get_request(request_id)


@router.patch("/requests/{request_id}", response_model=ProcurementRequestResponse)
async def update_request(request_id: str, update: ProcurementRequestUpdate):
    """Update a procurement request."""
    return await request_service.update_request(request_id, update)


@router.patch(
    "/requests/{request_id}/status", response_model=ProcurementRequestResponse
)
async def update_request_status(request_id: str, status_update: StatusUpdate):
    """Update the status of a procurement request."""
    return await request_service.update_status(request_id, status_update)


@router.delete("/requests/{request_id}")
async def delete_request(request_id: str):
    """Delete a procurement request."""
    return await request_service.delete_request(request_id)


@router.patch(
    "/requests/{request_id}/archive", response_model=ProcurementRequestResponse
)
async def archive_request(request_id: str):
    """Archive a procurement request."""
    return await request_service.set_archived(request_id, archived=True)


@router.patch(
    "/requests/{request_id}/unarchive", response_model=ProcurementRequestResponse
)
async def unarchive_request(request_id: str):
    """Unarchive a procurement request."""
    return await request_service.set_archived(request_id, archived=False)


@router.get("/requests/{request_id}/history", response_model=List[StatusHistoryEntry])
async def get_request_history(request_id: str):
    """Get the status history of a procurement request."""
    return await request_service.get_request_history(request_id)


@router.get("/stats")
async def get_stats():
    """Get procurement request statistics."""
    return await request_service.get_stats()

