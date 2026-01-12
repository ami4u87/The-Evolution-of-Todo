"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables
from app.routers import tasks
from app.routers import auth

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Evolution of Todo - Phase II Backend API",
    version="2.0.0",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Run on application startup."""
    create_db_and_tables()


@app.get("/")
def read_root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "message": "Todo API - Phase II",
        "version": "2.0.0",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include task management router
app.include_router(tasks.router)

# Include authentication router
app.include_router(auth.router)
