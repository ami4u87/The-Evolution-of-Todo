"""Database configuration and connection management."""

from sqlmodel import create_engine, Session, SQLModel
from app.config import settings


def get_engine_args() -> dict:
    """Get database engine arguments based on database type.

    - SQLite: Requires check_same_thread=False for FastAPI
    - PostgreSQL/Neon: Uses connection pooling with pre-ping
    """
    database_url = settings.database_url

    # SQLite-specific configuration
    if database_url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "echo": settings.debug,
        }

    # PostgreSQL/Neon configuration
    # Neon requires SSL (included in connection string as ?sslmode=require)
    # Use connection pooling appropriate for serverless
    return {
        "echo": settings.debug,
        "pool_pre_ping": True,  # Verify connections before use
        "pool_size": 5,  # Connection pool size
        "max_overflow": 10,  # Additional connections beyond pool_size
        "pool_recycle": 300,  # Recycle connections after 5 minutes (good for Neon)
    }


# Create database engine with appropriate configuration
engine = create_engine(settings.database_url, **get_engine_args())


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session
