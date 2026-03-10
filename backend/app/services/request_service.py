"""Service for procurement request business logic."""
from datetime import datetime
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
from app.database import get_database
from app.constants import COMMODITY_GROUPS
from app.models.request import (
    ProcurementRequestCreate,
    ProcurementRequestUpdate,
    StatusUpdate,
    RequestStatus,
    ProcurementRequestResponse,
    StatusHistoryEntry,
)


class RequestService:
    """Service for managing procurement requests."""

    @staticmethod
    def serialize_request(request: dict) -> dict:
        """Convert MongoDB document to response format."""
        request["id"] = str(request.pop("_id"))

        # Find commodity group name
        cg = next(
            (g for g in COMMODITY_GROUPS if g["id"] == request.get("commodity_group_id")),
            None,
        )
        request["commodity_group_name"] = cg["name"] if cg else "Unknown"
        request["archived"] = request.get("archived", False)

        return request

    @staticmethod
    def validate_commodity_group(commodity_group_id: str) -> None:
        """Validate that commodity group ID exists."""
        cg = next(
            (g for g in COMMODITY_GROUPS if g["id"] == commodity_group_id), None
        )
        if not cg:
            raise HTTPException(status_code=400, detail="Invalid commodity group ID")

    @staticmethod
    def validate_total_cost(order_lines: list, total_cost: float) -> None:
        """Validate that total cost matches sum of order lines."""
        calculated_total = sum(line.total_price for line in order_lines)
        if abs(calculated_total - total_cost) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Total cost ({total_cost}) doesn't match sum of order lines ({calculated_total})",
            )

    async def create_request(
        self, request: ProcurementRequestCreate
    ) -> ProcurementRequestResponse:
        """Create a new procurement request."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Validate
        self.validate_commodity_group(request.commodity_group_id)
        self.validate_total_cost(request.order_lines, request.total_cost)

        # Create the request document
        now = datetime.utcnow()
        request_doc = {
            **request.model_dump(),
            "order_lines": [line.model_dump() for line in request.order_lines],
            "status": RequestStatus.OPEN.value,
            "status_history": [
                {
                    "status": RequestStatus.OPEN.value,
                    "changed_at": now,
                    "changed_by": request.requestor_name,
                    "notes": "Request created",
                }
            ],
            "archived": False,
            "created_at": now,
            "updated_at": now,
        }

        result = await db["procurement_requests"].insert_one(request_doc)
        request_doc["_id"] = result.inserted_id

        return ProcurementRequestResponse(**self.serialize_request(request_doc))

    async def get_requests(
        self,
        status: Optional[RequestStatus] = None,
        department: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> list[ProcurementRequestResponse]:
        """Get all procurement requests with optional filtering."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        query = {}
        if status:
            query["status"] = status.value
        if department:
            query["department"] = department
        # Default to non-archived when not specified
        if archived is None:
            archived = False
        if archived:
            query["archived"] = True
        else:
            query["$or"] = [{"archived": False}, {"archived": {"$exists": False}}]

        cursor = db["procurement_requests"].find(query).sort("created_at", -1)
        requests = await cursor.to_list(length=None)

        return [
            ProcurementRequestResponse(**self.serialize_request(r)) for r in requests
        ]

    async def get_request(self, request_id: str) -> ProcurementRequestResponse:
        """Get a specific procurement request by ID."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        try:
            obj_id = ObjectId(request_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request ID format")

        request = await db["procurement_requests"].find_one({"_id": obj_id})
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        return ProcurementRequestResponse(**self.serialize_request(request))

    async def update_request(
        self, request_id: str, update: ProcurementRequestUpdate
    ) -> ProcurementRequestResponse:
        """Update a procurement request."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        try:
            obj_id = ObjectId(request_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request ID format")

        update_data = {k: v for k, v in update.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        if "order_lines" in update_data:
            update_data["order_lines"] = [
                line.model_dump() if hasattr(line, "model_dump") else line
                for line in update_data["order_lines"]
            ]

        update_data["updated_at"] = datetime.utcnow()

        result = await db["procurement_requests"].find_one_and_update(
            {"_id": obj_id}, {"$set": update_data}, return_document=True
        )

        if not result:
            raise HTTPException(status_code=404, detail="Request not found")

        return ProcurementRequestResponse(**self.serialize_request(result))

    async def update_status(
        self, request_id: str, status_update: StatusUpdate
    ) -> ProcurementRequestResponse:
        """Update the status of a procurement request."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        try:
            obj_id = ObjectId(request_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request ID format")

        # Get current request
        request = await db["procurement_requests"].find_one({"_id": obj_id})
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        # Create status history entry
        history_entry = {
            "status": status_update.status.value,
            "changed_at": datetime.utcnow(),
            "changed_by": status_update.changed_by,
            "notes": status_update.notes,
        }

        # Update the request
        result = await db["procurement_requests"].find_one_and_update(
            {"_id": obj_id},
            {
                "$set": {
                    "status": status_update.status.value,
                    "updated_at": datetime.utcnow(),
                },
                "$push": {"status_history": history_entry},
            },
            return_document=True,
        )

        return ProcurementRequestResponse(**self.serialize_request(result))

    async def delete_request(self, request_id: str) -> dict:
        """Delete a procurement request."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        try:
            obj_id = ObjectId(request_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request ID format")

        result = await db["procurement_requests"].delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Request not found")

        return {"message": "Request deleted successfully"}

    async def set_archived(
        self, request_id: str, archived: bool
    ) -> ProcurementRequestResponse:
        """Archive or unarchive a procurement request."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        try:
            obj_id = ObjectId(request_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request ID format")

        result = await db["procurement_requests"].find_one_and_update(
            {"_id": obj_id},
            {"$set": {"archived": archived, "updated_at": datetime.utcnow()}},
            return_document=True,
        )

        if not result:
            raise HTTPException(status_code=404, detail="Request not found")

        return ProcurementRequestResponse(**self.serialize_request(result))

    async def get_request_history(self, request_id: str) -> list[StatusHistoryEntry]:
        """Get the status history of a procurement request."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        try:
            obj_id = ObjectId(request_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request ID format")

        request = await db["procurement_requests"].find_one(
            {"_id": obj_id}, {"status_history": 1}
        )

        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        return [
            StatusHistoryEntry(**entry)
            for entry in request.get("status_history", [])
        ]

    async def get_stats(self) -> dict:
        """Get procurement request statistics."""
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_value": {"$sum": "$total_cost"},
                }
            }
        ]

        cursor = db["procurement_requests"].aggregate(pipeline)
        results = await cursor.to_list(length=None)

        stats = {
            "by_status": {
                r["_id"]: {"count": r["count"], "total_value": r["total_value"]}
                for r in results
            },
            "total_requests": sum(r["count"] for r in results),
            "total_value": sum(r["total_value"] for r in results),
        }

        return stats

