"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables
from app.events.publisher import EventPublisher
from app.routers import tasks
from app.routers import auth
from app.routers import chat

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Evolution of Todo - Phase V Backend API",
    version="5.0.0",
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

    # Initialize event publisher (Phase V)
    EventPublisher.configure(
        dapr_http_port=settings.dapr_http_port,
        enabled=settings.events_enabled,
    )


@app.get("/")
def read_root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "message": "Todo API - Phase V",
        "version": "5.0.0",
        "features": ["crud", "auth", "chat", "events"],
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "events_enabled": settings.events_enabled,
    }


# Include task management router
app.include_router(tasks.router)

# Include authentication router
app.include_router(auth.router)

# Include chat router (Phase III: AI Chatbot)
app.include_router(chat.router)
