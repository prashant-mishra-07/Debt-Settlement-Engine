"""
MongoDB Database Connection Utility
Handles all database operations for the Debt Settlement Engine
Uses AsyncIOMotorClient for async MongoDB operations
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseManager:
    """
    Async MongoDB connection manager for debt settlement operations
    
    Manages:
    - Group metadata storage
    - Transaction ledgers
    - Optimization results caching
    
    Note: This is a stub implementation for Phase 3.
    Full persistence implementation will be added in Phase 4.
    """
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_uri = os.getenv(
            "MONGODB_URI", 
            "mongodb://localhost:27017/"
        )
        self.db_name = os.getenv("DB_NAME", "debt_settlement")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """
        Establish connection to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            # Test connection
            await self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB: {self.db_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def insert_group(self, group_data: Dict) -> str:
        """
        Insert a new debt group into the database
        
        Args:
            group_data: Dictionary containing group_id, transactions, and metadata
            
        Returns:
            str: Inserted document ID
        """
        try:
            if not self.db:
                await self.connect()
            
            collection = self.db.groups
            result = await collection.insert_one(group_data)
            logger.info(f"Group inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert group: {e}")
            raise
    
    async def get_group(self, group_id: str) -> Optional[Dict]:
        """
        Retrieve a group by its ID
        
        Args:
            group_id: Unique group identifier
            
        Returns:
            Dict: Group data if found, None otherwise
        """
        try:
            if not self.db:
                await self.connect()
            
            collection = self.db.groups
            group_data = await collection.find_one({"group_id": group_id})
            
            if group_data:
                # Convert ObjectId to string for JSON serialization
                group_data["_id"] = str(group_data["_id"])
                return group_data
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve group: {e}")
            raise
    
    async def update_group_optimization(self, group_id: str, optimization_result: Dict) -> bool:
        """
        Update a group with optimization results
        
        Args:
            group_id: Group identifier
            optimization_result: Dictionary containing optimized transactions and metrics
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if not self.db:
                await self.connect()
            
            collection = self.db.groups
            result = await collection.update_one(
                {"group_id": group_id},
                {
                    "$set": {
                        "optimization_result": optimization_result,
                        "status": "optimized"
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Group {group_id} optimization updated")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update optimization: {e}")
            raise
    
    async def delete_group(self, group_id: str) -> bool:
        """
        Delete a group from the database
        
        Args:
            group_id: Group identifier
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            if not self.db:
                await self.connect()
            
            collection = self.db.groups
            result = await collection.delete_one({"group_id": group_id})
            
            if result.deleted_count > 0:
                logger.info(f"Group {group_id} deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete group: {e}")
            raise
    
    async def list_all_groups(self) -> List[Dict]:
        """
        List all groups in the database
        
        Returns:
            List[Dict]: List of all groups
        """
        try:
            if not self.db:
                await self.connect()
            
            collection = self.db.groups
            groups = await collection.find({}).to_list(length=None)
            
            # Convert ObjectIds to strings
            for group in groups:
                group["_id"] = str(group["_id"])
            
            return groups
        except Exception as e:
            logger.error(f"Failed to list groups: {e}")
            raise


# Singleton instance for application-wide use
db_manager = DatabaseManager()
