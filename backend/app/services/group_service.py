"""
Group service layer for MongoDB CRUD operations.
"""

from typing import Any, Dict, List, Optional

from app.models.group import Group
from app.models.transaction import Transaction
from database.db_connection import get_database


async def create_group(group: Group) -> Dict[str, Any]:
    db = get_database()
    group_data = group.dict()
    await db.groups.insert_one(group_data)
    return group_data


async def get_group(group_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    group_data = await db.groups.find_one({"group_id": group_id})
    if group_data:
        group_data["_id"] = str(group_data["_id"])
    return group_data


async def add_transaction_to_group(group_id: str, transaction: Transaction) -> Optional[Dict[str, Any]]:
    db = get_database()
    update_result = await db.groups.update_one(
        {"group_id": group_id},
        {
            "$push": {"raw_transactions": transaction.dict()},
            "$set": {"is_optimized": False, "optimized_transactions": []},
        },
    )
    if update_result.modified_count == 0:
        return None
    return await get_group(group_id)


async def update_group_optimized_status(group_id: str, optimized_transactions: List[Dict[str, Any]]) -> bool:
    db = get_database()
    result = await db.groups.update_one(
        {"group_id": group_id},
        {
            "$set": {
                "optimized_transactions": optimized_transactions,
                "is_optimized": True,
            }
        },
    )
    return result.modified_count > 0
