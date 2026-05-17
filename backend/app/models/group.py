"""
Pydantic models for debt group persistence and API payloads.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.models.transaction import Transaction


class Group(BaseModel):
    """Group metadata and transaction collection."""

    group_id: str = Field(..., description="Unique group identifier")
    name: str = Field(..., description="Human-readable group name")
    raw_transactions: List[Transaction] = Field(
        default_factory=list,
        description="Raw transactions that belong to the group"
    )
    optimized_transactions: List[Transaction] = Field(
        default_factory=list,
        description="Transactions produced by the optimizer"
    )
    is_optimized: bool = Field(
        default=False,
        description="Flag that indicates whether the group has been optimized"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp for the group"
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "group_id": "group_123",
                "name": "Family Debt Settlement",
                "raw_transactions": [
                    {"from_user": "alice", "to_user": "bob", "amount": 100.0}
                ],
                "optimized_transactions": [],
                "is_optimized": False,
                "created_at": "2026-05-17T12:00:00Z"
            }
        }
