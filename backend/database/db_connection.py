"""
MongoDB connection utilities for the Debt Settlement Engine.
"""

import os
import logging
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "debt_settlement")

client: Optional[AsyncIOMotorClient] = None
_db = None


async def connect_to_mongo() -> None:
    """Initialize the MongoDB connection on application startup."""
    global client, _db
    if client is not None and _db is not None:
        return

    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        await client.admin.command("ping")
        _db = client[DB_NAME]
        logger.info(f"Connected to MongoDB at {MONGODB_URI}, using database '{DB_NAME}'")
    except PyMongoError as exc:
        logger.error(f"Failed to connect to MongoDB: {exc}")
        raise


async def close_mongo_connection() -> None:
    """Close the MongoDB connection on application shutdown."""
    global client, _db
    if client is not None:
        client.close()
        logger.info("MongoDB connection closed")
        client = None
        _db = None


def get_database():
    """Return the active MongoDB database instance."""
    if _db is None:
        raise RuntimeError("MongoDB connection is not initialized. Call connect_to_mongo() first.")
    return _db
