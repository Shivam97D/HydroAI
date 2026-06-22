"""Async MongoDB client using Motor."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import get_settings

_client: Optional[AsyncIOMotorClient] = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client


def get_mongo_db() -> AsyncIOMotorDatabase:
    settings = get_settings()
    return get_mongo_client()[settings.MONGO_DB_NAME]
