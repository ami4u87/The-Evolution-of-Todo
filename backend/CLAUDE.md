# Backend Development Guidelines - Todo API

## Overview
This is the FastAPI backend for the Evolution of Todo application. It provides a REST API with JWT authentication, user data isolation, and PostgreSQL database integration using SQLModel.

## Tech Stack
- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT token verification
- **Python**: 3.13+
- **Package Manager**: UV
- **Validation**: Pydantic v2

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── config.py            # Settings via Pydantic Settings
│   ├── database.py          # Database engine and session
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py         # User model
│   │   └── task.py         # Task model
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── task.py         # Task DTOs
│   │   └── auth.py         # Auth DTOs
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   └── tasks.py        # Task endpoints
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   └── task_service.py # Task operations
│   ├── auth/                # Authentication utilities
│   │   ├── __init__.py
│   │   └── jwt.py          # JWT verification
│   └── dependencies.py      # FastAPI dependencies
├── tests/                   # Test files
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   └── test_tasks.py       # Task endpoint tests
├── pyproject.toml           # Dependencies and config
├── .env                     # Environment variables (git-ignored)
├── .env.example             # Environment template
└── README.md
```

## Development Principles

### 1. Spec-Driven Development
- All features must have specs in `/specs/api/` or `/specs/features/`
- Read and follow specs precisely
- No implementation without specs
- Verify implementation matches spec requirements

### 2. Layered Architecture
```
Request → Router → Service → Database
         ↓          ↓          ↓
     Validation  Logic    Persistence
```

- **Routers**: Handle HTTP requests/responses, validation, authentication
- **Services**: Contain business logic, reusable operations
- **Models**: SQLModel classes for database tables
- **Schemas**: Pydantic models for request/response validation

### 3. Authentication & Authorization
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt, JWTError
from app.config import settings

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthCredentials = Depends(security)
) -> str:
    """Extract and verify user_id from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

All protected endpoints must use `get_current_user_id` dependency.

### 4. Data Isolation
**CRITICAL**: Every database query MUST filter by authenticated user_id:

```python
# ✓ CORRECT
def get_user_tasks(user_id: str, session: Session):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

# ✗ WRONG - Returns all users' tasks
def get_tasks(session: Session):
    return session.exec(select(Task)).all()
```

### 5. SQLModel Models
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class Task(SQLModel, table=True):
    """Task database model."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    status: str = Field(default="pending", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 6. Pydantic Schemas (DTOs)
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class TaskCreate(BaseModel):
    """Request schema for creating a task."""
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None

class TaskUpdate(BaseModel):
    """Request schema for updating a task."""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = None

class TaskResponse(BaseModel):
    """Response schema for task data."""
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### 7. Router Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.auth.jwt import get_current_user_id
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Create a new task for the authenticated user."""
    service = TaskService(session)
    task = service.create_task(user_id, task_data)
    return task
```

### 8. Service Layer Pattern
```python
from sqlmodel import Session, select
from uuid import UUID
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    """Service layer for task operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_task(self, user_id: str, data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(
            user_id=UUID(user_id),
            title=data.title,
            description=data.description,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_user_tasks(self, user_id: str) -> list[Task]:
        """Get all tasks for a user."""
        return self.session.exec(
            select(Task).where(Task.user_id == UUID(user_id))
        ).all()

    def get_task(self, user_id: str, task_id: UUID) -> Task | None:
        """Get a specific task if owned by user."""
        return self.session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == UUID(user_id)
            )
        ).first()
```

### 9. Error Handling
```python
from fastapi import HTTPException, status

# 401 Unauthorized - Invalid/missing token
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials"
)

# 403 Forbidden - User doesn't own resource
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authorized to access this resource"
)

# 404 Not Found - Resource doesn't exist
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task not found"
)

# 422 Unprocessable Entity - Validation error (handled by FastAPI)

# 500 Internal Server Error - Unexpected errors
# Log error and return generic message
```

### 10. Environment Variables
Required in `.env`:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
BETTER_AUTH_SECRET=same-secret-as-frontend-min-32-chars
JWT_ALGORITHM=HS256
API_PREFIX=/api
DEBUG=false
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 11. Database Migrations (Future)
When schema changes are needed:
1. Update SQLModel models
2. Generate migration with Alembic (to be set up)
3. Apply migration to database
4. Update corresponding specs

### 12. Testing
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_token():
    # Generate test JWT token
    return "Bearer test_token_here"

def test_create_task(client, auth_token):
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "Test"},
        headers={"Authorization": auth_token}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
```

### 13. Code Quality
- Use type hints for all function parameters and returns
- Keep functions small and focused (single responsibility)
- Use descriptive variable names
- Add docstrings for public functions
- Follow PEP 8 via Ruff
- Avoid deep nesting (max 3 levels)

### 14. Security Checklist
- [ ] All endpoints verify JWT token
- [ ] All queries filter by authenticated user_id
- [ ] No sensitive data in logs
- [ ] Environment variables for secrets
- [ ] SQL injection prevented by SQLModel parameterization
- [ ] CORS configured correctly
- [ ] HTTPS in production

### 15. Performance
- Use database indexes on foreign keys and frequently queried columns
- Implement pagination for list endpoints
- Use connection pooling (configured in database.py)
- Lazy load relationships when not needed
- Monitor query performance with `echo=True` in development

## API Endpoints Reference

### Tasks
- `GET /api/tasks` - List tasks (paginated)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{task_id}` - Get task
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `PATCH /api/tasks/{task_id}/complete` - Mark complete

All endpoints:
- Require `Authorization: Bearer <token>` header
- Return 401 if token invalid
- Return 403 if resource not owned by user
- Return 404 if resource not found
- Return 422 for validation errors

## Development Workflow
1. Read spec from `/specs/api/` or `/specs/features/`
2. Create/update SQLModel models in `/app/models/`
3. Create Pydantic schemas in `/app/schemas/`
4. Implement service logic in `/app/services/`
5. Create router endpoints in `/app/routers/`
6. Register router in `main.py`
7. Write tests in `/tests/`
8. Run tests and verify
9. Test integration with frontend

## Running the Server
```bash
# Development with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Common Tasks

### Adding a New Model
1. Create model file in `/app/models/`
2. Import in `/app/models/__init__.py`
3. Create corresponding schemas in `/app/schemas/`
4. Add foreign key relationships if needed
5. Run database migration (when Alembic set up)

### Adding a New Endpoint
1. Check spec for requirements
2. Create/update schemas for request/response
3. Implement service method
4. Create router endpoint with authentication
5. Test with curl or httpx
6. Verify in interactive docs (/docs)

### Debugging Database Issues
1. Enable query logging: `echo=True` in database.py
2. Check connection string in .env
3. Verify tables exist: connect with psql
4. Check foreign key constraints
5. Review SQLModel query syntax

## Monorepo Context
- Part of monorepo with Next.js frontend
- Backend runs on http://localhost:8000
- Frontend on http://localhost:3000
- Shared authentication secret in both .env files
- API specs in `/specs/api/`
- Database specs in `/specs/database/`

## Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python JWT Documentation](https://python-jose.readthedocs.io/)

## Critical Reminders
1. **ALWAYS filter by user_id** in database queries
2. **ALWAYS verify JWT** on protected endpoints
3. **NEVER expose secrets** in code or logs
4. **ALWAYS use Pydantic** for validation
5. **FOLLOW specs precisely** - this is spec-driven development
