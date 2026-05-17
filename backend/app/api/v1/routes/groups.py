"""
API routes for group persistence and transaction management.
"""

from fastapi import APIRouter, HTTPException, status

from app.models.group import Group
from app.models.transaction import Transaction
from app.services.group_service import (
    add_transaction_to_group,
    create_group,
    get_group,
)

router = APIRouter()


@router.post("/groups", response_model=Group, status_code=status.HTTP_201_CREATED)
async def create_group_route(group: Group):
    """Create a new group with raw transactions."""
    existing_group = await get_group(group.group_id)
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Group with ID '{group.group_id}' already exists.",
        )

    created_group = await create_group(group)
    return created_group


@router.get("/groups/{group_id}", response_model=Group)
async def get_group_route(group_id: str):
    """Retrieve a group and its transactions."""
    group_data = await get_group(group_id)
    if not group_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group '{group_id}' not found.",
        )
    return group_data


@router.post("/groups/{group_id}/transactions", response_model=Group)
async def add_transaction_to_group_route(group_id: str, transaction: Transaction):
    """Append a transaction to an existing group and reset optimization state."""
    group_data = await get_group(group_id)
    if not group_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group '{group_id}' not found.",
        )

    updated_group = await add_transaction_to_group(group_id, transaction)
    if not updated_group:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add transaction to group.",
        )

    return updated_group
