"""Main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.database import connect_to_mongo, close_mongo_connection, seed_database
from app.services.ai_service import AIService
from app.routes import api_router

# Initialize FastAPI app
app = FastAPI(title="Procurement Request Management API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Initialize services
ai_service = AIService()


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    await connect_to_mongo()
    await seed_database()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    await close_mongo_connection()


@app.get("/")
async def read_root():
    """Root endpoint."""
    return {"message": "Procurement Request Management API"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from app.database import get_database

    db = get_database()
    db_status = "connected" if db is not None else "disconnected"
    openai_status = "configured" if ai_service.is_available() else "not configured"

    return {"status": "healthy", "database": db_status, "openai": openai_status}
