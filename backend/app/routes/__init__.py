"""Routes package."""
from fastapi import APIRouter
from app.routes import requests, metadata, ai, chat, conversations

# Create main router
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(requests.router, tags=["requests"])
api_router.include_router(metadata.router, tags=["metadata"])
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(conversations.router, tags=["conversations"])

__all__ = ["api_router"]

