"""Routes for metadata (commodity groups, departments)."""
from typing import List
from fastapi import APIRouter
from app.models.metadata import CommodityGroup
from app.constants import COMMODITY_GROUPS, DEPARTMENTS

router = APIRouter()


@router.get("/commodity-groups", response_model=List[CommodityGroup])
async def get_commodity_groups():
    """Get all commodity groups."""
    return [CommodityGroup(**cg) for cg in COMMODITY_GROUPS]


@router.get("/departments", response_model=List[str])
async def get_departments():
    """Get all departments."""
    return DEPARTMENTS

