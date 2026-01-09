# Backend Quick Start Guide

Get the Todo API up and running in 5 minutes!

## Prerequisites

- Python 3.13+
- UV package manager
- PostgreSQL (Docker or local)

## Step 1: Install Dependencies

```bash
cd backend
uv pip install -e .
```

## Step 2: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env  # or use your favorite editor
```

Required environment variables:
```bash
DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your-shared-secret-key-min-32-characters-long
```

## Step 3: Start Database

### Option A: Docker Compose (Recommended)
```bash
# From project root
docker-compose up postgres

# Or run all services
docker-compose up
```

### Option B: Local PostgreSQL
```bash
# Create database
createdb todo_db

# Or with psql
psql -U postgres -c "CREATE DATABASE todo_db;"
```

### Option C: Neon (Production)
1. Sign up at https://neon.tech
2. Create new project
3. Copy connection string to DATABASE_URL

## Step 4: Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 5: Test API

### Test health endpoint
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Todo API - Phase II",
  "version": "2.0.0"
}
```

### View interactive docs
Open browser: http://localhost:8000/docs

## Step 6: Get JWT Token

For authenticated endpoints, you need a JWT token:

### Option A: From Frontend (Recommended)
1. Start frontend: `cd frontend && npm run dev`
2. Sign up/login at http://localhost:3000
3. Get token from Better Auth

### Option B: Generate Test Token
```python
# Run in Python shell
from jose import jwt
import datetime

payload = {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
}

token = jwt.encode(payload, "your-secret-key", algorithm="HS256")
print(f"Token: {token}")
```

## Step 7: Test Authenticated Endpoints

```bash
# Set token
export TOKEN="your_jwt_token_here"

# List tasks
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task", "description": "Testing the API"}'
```

## Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Reinstall dependencies
uv pip install -e .
```

### Error: "Could not connect to database"
```bash
# Check database is running
docker ps  # Should see postgres container

# Or check local PostgreSQL
pg_isready
```

### Error: "Invalid token"
```bash
# Verify BETTER_AUTH_SECRET matches frontend
# Check token is not expired
# Ensure no extra quotes/spaces in token
```

### Port 8000 already in use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

## Development Tips

### Auto-reload on code changes
The `--reload` flag automatically restarts the server when code changes.

### Debug mode
Set `DEBUG=true` in `.env` to see SQL queries and detailed errors.

### Interactive Python shell
```bash
# From backend directory
python

>>> from app.database import engine
>>> from sqlmodel import Session, select
>>> from app.models import Task
>>>
>>> with Session(engine) as session:
...     tasks = session.exec(select(Task)).all()
...     print(tasks)
```

### Database inspection
```bash
# Connect to database
psql $DATABASE_URL

# List tables
\dt

# Describe tasks table
\d tasks

# Query tasks
SELECT * FROM tasks;
```

## Next Steps

1. ✅ Backend running
2. ✅ Database connected
3. ✅ Endpoints accessible
4. ⏳ Start frontend
5. ⏳ Test full stack integration
6. ⏳ Build UI components

## Resources

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Testing Guide**: `TESTING.md`
- **Implementation Details**: `IMPLEMENTATION.md`
- **API Spec**: `/specs/api/endpoints.md`

---

**Need help?** Check `TESTING.md` for detailed examples!
