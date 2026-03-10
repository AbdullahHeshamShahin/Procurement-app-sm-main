"""Database configuration and utilities."""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import MONGODB_URI, MONGODB_DB_NAME
from app.constants import COMMODITY_GROUPS

# Global database client and database instance
mongo_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    """Create MongoDB client and database connection."""
    global mongo_client, db
    mongo_client = AsyncIOMotorClient(MONGODB_URI)
    db = mongo_client[MONGODB_DB_NAME]
    return db


async def close_mongo_connection():
    """Close MongoDB client connection."""
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()


async def seed_database():
    """Seed MongoDB with commodity groups if not present."""
    if db is None:
        return

    commodity_groups_collection = db["commodity_groups"]

    if await commodity_groups_collection.count_documents({}) == 0:
        await commodity_groups_collection.insert_many(COMMODITY_GROUPS)


def get_database():
    """Get the database instance."""
    return db
