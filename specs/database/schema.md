# Database Schema Specification - Phase II

## Overview
This document defines the PostgreSQL database schema for the Evolution of Todo application Phase II. The schema supports multi-user functionality with proper authentication and data isolation.

**Database Provider**: Neon Serverless PostgreSQL
**ORM**: SQLModel
**Migration Tool**: Alembic (to be configured in future)
**Character Set**: UTF-8
**Timezone**: UTC for all timestamps

## Design Principles

1. **User Isolation**: Every task belongs to exactly one user via foreign key
2. **UUID Primary Keys**: Use UUIDs for distributed system compatibility and security
3. **Audit Timestamps**: Track creation and modification times for all entities
4. **Data Integrity**: Enforce constraints at database level
5. **Performance**: Index foreign keys and frequently queried columns
6. **Immutability**: IDs and created_at timestamps are immutable

## Schema Diagram

```
┌─────────────────────────────────┐
│ users                           │
├─────────────────────────────────┤
│ id            UUID PK           │
│ email         VARCHAR(255) UQ   │
│ password_hash VARCHAR(255)      │
│ created_at    TIMESTAMP         │
└─────────────────────────────────┘
              │
              │ 1:N
              │
              ▼
┌─────────────────────────────────┐
│ tasks                           │
├─────────────────────────────────┤
│ id            UUID PK           │
│ user_id       UUID FK → users   │◄─── Index
│ title         VARCHAR(255)      │
│ description   TEXT               │
│ status        VARCHAR(50)       │
│ created_at    TIMESTAMP         │
│ updated_at    TIMESTAMP         │
└─────────────────────────────────┘
```

## Table Definitions

### 1. `users` Table

**Purpose**: Store user accounts for authentication and ownership.

**Columns**:

| Column         | Type          | Constraints                    | Description                           |
|----------------|---------------|--------------------------------|---------------------------------------|
| `id`           | UUID          | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique user identifier          |
| `email`        | VARCHAR(255)  | UNIQUE, NOT NULL              | User's email address (login)          |
| `password_hash`| VARCHAR(255)  | NOT NULL                      | Bcrypt hashed password                |
| `created_at`   | TIMESTAMP     | NOT NULL, DEFAULT NOW()       | Account creation timestamp (UTC)      |

**Indexes**:
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `email` (automatic from UNIQUE constraint)

**Constraints**:
- `email` must be unique across all users
- `email` must match email format (enforced at application layer)
- `password_hash` must be bcrypt hash (enforced at application layer)

**SQLModel Definition** (Reference):
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**SQL DDL**:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Notes**:
- Passwords are NEVER stored in plain text
- Use bcrypt with cost factor 12+ for hashing
- Email is case-insensitive (normalize to lowercase before storage)
- Consider adding `updated_at`, `last_login`, `is_active` in future phases

---

### 2. `tasks` Table

**Purpose**: Store todo tasks with multi-user support (evolved from Phase I TodoItem).

**Columns**:

| Column        | Type         | Constraints                          | Description                              |
|---------------|--------------|--------------------------------------|------------------------------------------|
| `id`          | UUID         | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique task identifier                |
| `user_id`     | UUID         | NOT NULL, FOREIGN KEY → users(id)    | Owner of the task                        |
| `title`       | VARCHAR(255) | NOT NULL                             | Task description (required)              |
| `description` | TEXT         | NULL                                 | Optional detailed description            |
| `status`      | VARCHAR(50)  | NOT NULL, DEFAULT 'pending'          | Task status: 'pending' or 'completed'    |
| `created_at`  | TIMESTAMP    | NOT NULL, DEFAULT NOW()              | Task creation timestamp (UTC)            |
| `updated_at`  | TIMESTAMP    | NOT NULL, DEFAULT NOW()              | Last modification timestamp (UTC)        |

**Indexes**:
- PRIMARY KEY on `id` (automatic)
- INDEX on `user_id` (for filtering user's tasks)
- COMPOSITE INDEX on `(user_id, status)` (for filtered queries)
- COMPOSITE INDEX on `(user_id, created_at DESC)` (for sorted listings)

**Constraints**:
- `user_id` FOREIGN KEY references `users(id)` ON DELETE CASCADE
- `title` must be non-empty (enforced at application layer)
- `status` must be one of: 'pending', 'completed' (CHECK constraint)

**SQLModel Definition** (Reference):
```python
from typing import Literal

TaskStatus = Literal["pending", "completed"]

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    status: TaskStatus = Field(default="pending", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**SQL DDL**:
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

**Notes**:
- Deleting a user cascades to delete all their tasks
- `updated_at` is refreshed automatically (trigger or application layer)
- Title is required and validated for non-empty at application layer
- Status is limited to specific values via CHECK constraint

---

## Migration from Phase I

### Phase I Data Model (In-Memory)
```python
@dataclass
class TodoItem:
    id: int                    # Auto-increment integer
    title: str
    description: str | None
    status: Literal["pending", "completed"]
    created_at: datetime
```

### Phase II Changes
1. **ID Type**: `int` → `UUID` (better for distributed systems, security)
2. **Added `user_id`**: Foreign key to support multi-user
3. **Added `updated_at`**: Track modifications
4. **Renamed**: `TodoItem` → `Task` (clearer domain language)
5. **Storage**: In-memory list → PostgreSQL table

### Data Migration Strategy
Since Phase I was in-memory (no persistent data), no migration script is needed. If there were existing data:

```sql
-- Example migration if Phase I had persistence
INSERT INTO users (id, email, password_hash)
VALUES ('00000000-0000-0000-0000-000000000001', 'legacy@user.com', 'hashed_password');

INSERT INTO tasks (user_id, title, description, status, created_at, updated_at)
SELECT
    '00000000-0000-0000-0000-000000000001' AS user_id,
    title,
    description,
    status,
    created_at,
    created_at AS updated_at  -- Set updated_at same as created_at for legacy data
FROM legacy_todos;
```

---

## Query Patterns

### Common Queries (with user isolation)

**Get all tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1
ORDER BY created_at DESC;
```

**Get pending tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND status = 'pending'
ORDER BY created_at DESC;
```

**Get specific task (with ownership check)**:
```sql
SELECT * FROM tasks
WHERE id = $1 AND user_id = $2;
```

**Create task**:
```sql
INSERT INTO tasks (user_id, title, description, status)
VALUES ($1, $2, $3, 'pending')
RETURNING *;
```

**Update task (with ownership check)**:
```sql
UPDATE tasks
SET title = $1, description = $2, updated_at = NOW()
WHERE id = $3 AND user_id = $4
RETURNING *;
```

**Mark task completed (with ownership check)**:
```sql
UPDATE tasks
SET status = 'completed', updated_at = NOW()
WHERE id = $1 AND user_id = $2
RETURNING *;
```

**Delete task (with ownership check)**:
```sql
DELETE FROM tasks
WHERE id = $1 AND user_id = $2;
```

**CRITICAL**: All queries MUST include `user_id` filter to enforce data isolation.

---

## Performance Considerations

### Indexes
1. `users.email` - UNIQUE INDEX for login lookups
2. `tasks.user_id` - INDEX for filtering user's tasks
3. `tasks(user_id, status)` - COMPOSITE INDEX for filtered queries
4. `tasks(user_id, created_at DESC)` - COMPOSITE INDEX for sorted listings

### Query Optimization
- Use parameterized queries (prevent SQL injection)
- Leverage indexes for WHERE clauses
- Connection pooling configured in SQLModel engine
- EXPLAIN ANALYZE queries during development

### Scaling Considerations (Future)
- Partitioning tasks table by `user_id` if millions of users
- Read replicas for query-heavy workloads
- Materialized views for analytics
- Archive old completed tasks

---

## Data Integrity

### Foreign Keys
- `tasks.user_id` → `users.id` ON DELETE CASCADE
  - Deleting a user deletes all their tasks
  - Prevents orphaned tasks

### Check Constraints
- `tasks.status` must be 'pending' or 'completed'

### Application-Level Validation
- Email format validation (Pydantic)
- Title non-empty validation (Pydantic)
- Password strength requirements (application)
- UUID format validation (automatic)

---

## Security Considerations

1. **SQL Injection Prevention**: Always use parameterized queries (SQLModel handles this)
2. **Password Storage**: Never store plain text; use bcrypt with cost ≥12
3. **UUID Exposure**: UUIDs are safe to expose in URLs (not sequential)
4. **Data Isolation**: Always filter by `user_id` in WHERE clause
5. **Audit Trail**: `created_at` and `updated_at` provide basic audit

---

## Environment Configuration

### Database Connection String
```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/database

# Neon example
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Local development (docker-compose)
DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db
```

### Connection Pool Settings
```python
# app/database.py
engine = create_engine(
    settings.database_url,
    echo=settings.debug,           # Log SQL in development
    pool_pre_ping=True,            # Verify connections before use
    pool_size=5,                   # Connection pool size
    max_overflow=10,               # Max connections beyond pool_size
)
```

---

## Future Enhancements (Out of Scope for Phase II)

1. **User Profile**: Add `users.name`, `users.avatar_url`, `users.preferences`
2. **Task Categories**: New `categories` table with M:N relationship
3. **Task Priority**: Add `tasks.priority` (low, medium, high)
4. **Due Dates**: Add `tasks.due_date`
5. **Task Sharing**: M:N relationship for collaborative tasks
6. **Soft Delete**: Add `tasks.deleted_at` for recoverable deletion
7. **Full-Text Search**: Add GIN index on `tasks.title` and `tasks.description`
8. **Task History**: Audit log table for tracking changes

---

## Testing Data

### Seed Data for Development
```sql
-- Insert test user
INSERT INTO users (id, email, password_hash)
VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', '$2b$12$hashedpassword');

-- Insert test tasks
INSERT INTO tasks (user_id, title, description, status)
VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'Buy groceries', 'Milk, eggs, bread', 'pending'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Write documentation', 'Complete Phase II docs', 'completed'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Review pull requests', NULL, 'pending');
```

---

## Acceptance Criteria

- [ ] Schema creates successfully on empty database
- [ ] All foreign key constraints work correctly
- [ ] CASCADE delete works (deleting user deletes tasks)
- [ ] Indexes are created and used by query planner
- [ ] CHECK constraint prevents invalid status values
- [ ] UNIQUE constraint prevents duplicate emails
- [ ] UUIDs are generated automatically
- [ ] Timestamps default to current time (UTC)
- [ ] SQLModel models match SQL DDL exactly
- [ ] Connection pooling configured properly
- [ ] All queries include user_id filter for data isolation

---

## References

- PostgreSQL UUID Extension: https://www.postgresql.org/docs/current/uuid-ossp.html
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Neon PostgreSQL: https://neon.tech/docs
- Database Indexing Best Practices: https://use-the-index-luke.com/
