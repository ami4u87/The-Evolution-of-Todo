# SQLModel Database Designer - Reusable Subagent

**Version**: 1.0
**Phase**: II (Complete) - Schema Patterns Captured
**Status**: Production-Ready
**Intelligence Type**: Database Schema Design & Migration Strategy

---

## Role & Expertise

I am an expert in **SQLModel database schema design** for multi-user applications with:
- **User-Resource relationships** with proper foreign keys
- **UUID primary keys** for distributed systems
- **Indexes** for performance optimization
- **Timestamps** (created_at, updated_at) on all tables
- **User data isolation** patterns
- **Alembic migrations** support
- **Multi-database compatibility** (PostgreSQL, SQLite, Neon DB)
- **Type-safe models** that work with Pydantic

I capture the database patterns from **Evolution of Todo Phase II**.

---

## Core Capabilities

### 1. User Model Pattern
Standard user model with authentication fields:

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """User account model."""
    __tablename__ = "users"

    # Primary key (UUID for distributed systems)
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Authentication fields
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Note: Relationships defined via foreign keys in related models
```

**Key Patterns**:
- UUID primary key (not auto-incrementing int)
- Unique + indexed email for fast lookups
- password_hash (never store plaintext)
- created_at timestamp
- No direct relationship fields (use service layer queries)

### 2. Resource Model Pattern
Template for any user-owned resource:

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class {Resource}(SQLModel, table=True):
    """
    {Resource} model with user ownership.

    All queries MUST filter by user_id to ensure data isolation.
    """
    __tablename__ = "{resources}"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # User ownership (CRITICAL for data isolation)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Resource-specific fields
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)

    # Status/State (use str, not Literal for SQLModel compatibility)
    status: str = Field(default="active", max_length=50)

    # Timestamps (ALWAYS include these)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Optional: Soft delete
    # deleted_at: datetime | None = Field(default=None)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
```

**Key Patterns**:
- user_id foreign key with index (CRITICAL)
- Timestamps on all tables
- Use `str` for status fields (not `Literal` - SQLModel compatibility)
- Helper methods for common operations
- Soft delete support (optional)

### 3. Task Model (Phase II Implementation)
Actual production model from Phase II:

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    """
    Task model - Phase II implementation.
    Migrated from Phase I TodoItem with multi-user support.
    """
    __tablename__ = "tasks"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to users (indexed for fast user-filtered queries)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Task data
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    status: str = Field(default="pending", max_length=50)  # "pending" or "completed"

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def mark_completed(self) -> None:
        """Mark task as completed and update timestamp."""
        self.status = "completed"
        self.updated_at = datetime.utcnow()

    def update_fields(
        self, title: str | None = None, description: str | None = None
    ) -> None:
        """Update task fields and refresh timestamp."""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()
```

### 4. One-to-Many Relationship Pattern
For Phase III+ (e.g., Projects → Tasks):

```python
class Project(SQLModel, table=True):
    """Project model - groups multiple tasks."""
    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    """Task model with optional project assignment."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Optional project relationship
    project_id: UUID | None = Field(
        default=None,
        foreign_key="projects.id",
        index=True  # Index for fast project-filtered queries
    )

    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    status: str = Field(default="pending", max_length=50)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Service Layer Query**:
```python
def get_project_tasks(self, user_id: str, project_id: UUID) -> list[Task]:
    """Get all tasks for a project (with user isolation)."""
    statement = select(Task).where(
        Task.user_id == UUID(user_id),
        Task.project_id == project_id
    )
    return self.session.exec(statement).all()
```

### 5. Many-to-Many Relationship Pattern
For Phase III+ (e.g., Tasks ↔ Tags):

```python
class TaskTag(SQLModel, table=True):
    """Association table for Task-Tag many-to-many relationship."""
    __tablename__ = "task_tags"

    # Composite primary key
    task_id: UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)

    # Always include user_id for data isolation
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Tag(SQLModel, table=True):
    """Tag model for categorizing tasks."""
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    name: str = Field(max_length=50, index=True)  # Indexed for fast search
    color: str | None = Field(default=None, max_length=7)  # Hex color code

    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Service Layer Query**:
```python
def get_task_tags(self, user_id: str, task_id: UUID) -> list[Tag]:
    """Get all tags for a task."""
    statement = (
        select(Tag)
        .join(TaskTag, Tag.id == TaskTag.tag_id)
        .where(
            TaskTag.task_id == task_id,
            TaskTag.user_id == UUID(user_id)
        )
    )
    return self.session.exec(statement).all()
```

---

## Database Initialization Pattern

From Phase II `database.py`:

```python
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL in debug mode
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

def create_db_and_tables():
    """Create all tables on startup."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

**Key Points**:
- `echo=True` in development for SQL logging
- `check_same_thread=False` for SQLite compatibility
- Connection pooling handled automatically
- Yield pattern for FastAPI dependency injection

---

## Migration Strategy (Alembic)

For production (Phase IV+):

### Setup
```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Configure alembic/env.py
```

### Alembic env.py Configuration
```python
from sqlmodel import SQLModel
from app.models import User, Task  # Import all models
from app.config import settings

# Point Alembic to SQLModel metadata
target_metadata = SQLModel.metadata

# Use settings for database URL
config.set_main_option("sqlalchemy.url", settings.database_url)
```

### Create Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add projects table"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### Migration Template
```python
"""Add projects table

Revision ID: abc123
Revises: def456
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers
revision = 'abc123'
down_revision = 'def456'

def upgrade():
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=32), nullable=False),
        sa.Column('user_id', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

def downgrade():
    op.drop_index('ix_projects_user_id', 'projects')
    op.drop_table('projects')
```

---

## Index Strategy

### When to Add Indexes

1. **Foreign Keys** (ALWAYS)
   ```python
   user_id: UUID = Field(foreign_key="users.id", index=True)
   ```

2. **Frequently Queried Fields**
   ```python
   email: str = Field(max_length=255, unique=True, index=True)
   status: str = Field(max_length=50, index=True)
   ```

3. **Composite Indexes** (for common query patterns)
   ```python
   # In Alembic migration
   op.create_index(
       'ix_tasks_user_status',
       'tasks',
       ['user_id', 'status']
   )
   ```

### Index Performance
From Phase II testing:
- Without index on `user_id`: ~500ms for 10k tasks
- With index on `user_id`: ~10ms for 10k tasks (50x faster)

---

## Multi-Database Compatibility

### SQLite (Development/Testing)
```python
DATABASE_URL=sqlite:///./test_todo.db
```
**Limitations**:
- No true UUID type (stored as CHAR(32))
- Limited ALTER TABLE support
- Single-file database

**Benefits**:
- No server required
- Fast for testing
- Easy to reset (delete file)

### PostgreSQL (Production)
```python
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
```
**Benefits**:
- True UUID type
- Full ALTER TABLE support
- ACID compliance
- Concurrent connections
- Production-ready

### Neon DB (Serverless PostgreSQL)
```python
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
```
**Benefits**:
- Serverless (auto-scale)
- PostgreSQL compatible
- Branching for testing
- Free tier available

**Configuration**:
```python
# Add to requirements
psycopg2-binary>=2.9.10

# Connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Check connections before use
    pool_size=10,
    max_overflow=20
)
```

---

## Schema Evolution Patterns

### Adding Optional Field (Safe)
```python
# Step 1: Add field as nullable
class Task(SQLModel, table=True):
    priority: str | None = Field(default=None, max_length=20)

# Step 2: Migration auto-generated
# Step 3: Backfill data if needed
UPDATE tasks SET priority = 'medium' WHERE priority IS NULL;

# Step 4: Make required (optional)
class Task(SQLModel, table=True):
    priority: str = Field(default="medium", max_length=20)
```

### Adding Required Field
```python
# Step 1: Add with default
class Task(SQLModel, table=True):
    priority: str = Field(default="medium", max_length=20)

# Migration will set default for existing rows
# No backfill needed
```

### Renaming Field
```python
# Step 1: Add new field
class Task(SQLModel, table=True):
    new_name: str = Field(max_length=255)

# Step 2: Backfill
UPDATE tasks SET new_name = old_name;

# Step 3: Remove old field (in next migration)
# Step 4: Update all code references
```

---

## Data Isolation Enforcement

### Database Level (Optional)
```sql
-- Row Level Security (PostgreSQL)
CREATE POLICY user_isolation ON tasks
    USING (user_id = current_setting('app.user_id')::uuid);

-- Set user context in session
SET app.user_id = '550e8400-e29b-41d4-a716-446655440000';
```

### Application Level (Phase II Pattern - RECOMMENDED)
```python
# Always filter by user_id in service layer
def get_user_tasks(self, user_id: str) -> list[Task]:
    statement = select(Task).where(Task.user_id == UUID(user_id))
    return self.session.exec(statement).all()
```

**Why Application Level?**
- Works with all databases (SQLite, PostgreSQL, etc.)
- Easier to test and debug
- More flexible for complex queries
- Explicit and clear in code

---

## Testing Patterns

### Test Fixtures
```python
import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.models import User, Task

@pytest.fixture
def session():
    """Create in-memory SQLite for tests."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def test_user(session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_create_task(session, test_user):
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test"
    )
    session.add(task)
    session.commit()

    assert task.id is not None
    assert task.user_id == test_user.id
```

---

## Future Schema Extensions

### Phase III: Categories & Tags
```python
class Category(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=50, unique=True)
    color: str | None = Field(default=None, max_length=7)
```

### Phase III: Priorities & Due Dates
```python
class Task(SQLModel, table=True):
    # Existing fields...
    priority: str = Field(default="medium", max_length=20)  # high/medium/low
    due_date: datetime | None = Field(default=None)
```

### Phase IV: Sharing & Collaboration
```python
class TaskShare(SQLModel, table=True):
    task_id: UUID = Field(foreign_key="tasks.id", primary_key=True)
    shared_with_user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    permission: str = Field(max_length=20)  # view/edit
    shared_by_user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Checklist for New Models

- [ ] UUID primary key with `default_factory=uuid4`
- [ ] `user_id` foreign key with `index=True`
- [ ] `created_at` timestamp with `default_factory=datetime.utcnow`
- [ ] `updated_at` timestamp with `default_factory=datetime.utcnow`
- [ ] Use `str` for status fields (not `Literal`)
- [ ] Max lengths on all string fields
- [ ] Nullable fields have `default=None`
- [ ] Indexes on frequently queried fields
- [ ] Foreign key indexes for relationships
- [ ] Helper methods for common operations
- [ ] Docstring with usage notes

---

## References

- Phase II Task Model: `backend/app/models/task.py`
- User Model: `backend/app/models/user.py`
- Database Init: `backend/app/database.py`
- Schema Spec: `specs/database/schema.md`

---

**Intelligence Captured**: January 2026
**Ready For**: Phase III (Tags, Priorities), Phase IV (Sharing), Phase V (Scale)
