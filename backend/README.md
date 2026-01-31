# Todo Backend API - Phase II

FastAPI backend for the Evolution of Todo application with multi-user support, authentication, and PostgreSQL database.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT token verification
- **Python**: 3.13+
- **Package Manager**: UV

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Settings and configuration
│   ├── database.py       # Database connection
│   ├── models/           # SQLModel models (to be created)
│   ├── routers/          # API route handlers (to be created)
│   ├── services/         # Business logic (to be created)
│   └── auth/             # Authentication utilities (to be created)
├── tests/                # Test files (to be created)
├── pyproject.toml        # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Setup

### Prerequisites

- Python 3.13+
- UV package manager
- PostgreSQL database (Neon recommended for production, Docker for local dev)

### Database Setup

#### Option 1: Neon Serverless PostgreSQL (Recommended for Production)

1. Create a free account at [Neon](https://console.neon.tech)
2. Create a new project
3. Copy the connection string from the dashboard (it looks like):
   ```
   postgresql://neondb_owner:xxxx@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Set `DATABASE_URL` in your `.env` file to this connection string

**Neon Benefits:**
- Free tier with 0.5 GB storage
- Serverless auto-scaling
- Automatic backups
- Branch databases for development
- No server management

#### Option 2: Local PostgreSQL with Docker

```bash
# Start PostgreSQL container
docker-compose up postgres -d

# Connection string (automatically configured):
# DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db
```

#### Option 3: SQLite (Quick Local Testing Only)

For quick local testing without Docker:
```
DATABASE_URL=sqlite:///./test_todo.db
```
**Note:** SQLite is NOT recommended for production due to lack of concurrent write support.

### Installation

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your configuration:
   - Set `DATABASE_URL` to your database connection string (see Database Setup above)
   - Set `BETTER_AUTH_SECRET` (same secret as frontend, minimum 32 characters)

3. Install dependencies using UV:
   ```bash
   uv pip install -e .
   ```

4. For development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Tasks API (to be implemented)
All endpoints require `Authorization: Bearer <jwt_token>` header:

- `GET /api/tasks` - List all tasks for authenticated user
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{task_id}` - Get specific task
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `PATCH /api/tasks/{task_id}/complete` - Mark task as complete

## Authentication

The backend verifies JWT tokens issued by Better Auth on the frontend:

1. Frontend sends JWT token in `Authorization: Bearer <token>` header
2. Backend verifies token signature using shared `BETTER_AUTH_SECRET`
3. Backend extracts `user_id` from token claims
4. All database queries filter by `user_id` for data isolation

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Development Guidelines

1. **Spec-Driven**: All features must have specs in `/specs/`
2. **Type Safety**: Use Pydantic and SQLModel for validation
3. **Authentication**: All endpoints verify JWT and filter by user_id
4. **Error Handling**: Return appropriate HTTP status codes
5. **Testing**: Write tests for all endpoints
6. **Code Quality**: Use Ruff for linting

## Testing

Run tests (when implemented):
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Linting

Format and lint code:
```bash
ruff format .
ruff check .
```

## Docker

The backend can be run via Docker Compose (see root `docker-compose.yml`):
```bash
docker-compose up backend
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string (Neon, PostgreSQL, or SQLite) |
| `BETTER_AUTH_SECRET` | Yes | Shared secret with frontend for JWT verification (min 32 chars) |
| `JWT_ALGORITHM` | No | JWT algorithm (default: HS256) |
| `API_PREFIX` | No | API route prefix (default: /api) |
| `DEBUG` | No | Enable debug mode (default: false) |
| `CORS_ORIGINS` | No | Allowed CORS origins (default: http://localhost:3000) |
| `AI_PROVIDER` | No | AI provider for chat: "groq" or "openai" |
| `GROQ_API_KEY` | No | Groq API key (free at https://console.groq.com) |
| `OPENAI_API_KEY` | No | OpenAI API key |

See `.env.example` for detailed configuration options.

## Contributing

This is a spec-driven project. All changes must:
1. Have a corresponding spec in `/specs/`
2. Follow the architecture defined in `/specs/architecture.md`
3. Be coordinated with frontend changes
4. Include tests

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [UV Documentation](https://github.com/astral-sh/uv)
