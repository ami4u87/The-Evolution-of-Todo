# Backend API Testing Guide

This guide explains how to test the Todo API endpoints.

## Prerequisites

1. **Backend running**: `uvicorn app.main:app --reload`
2. **Database running**: PostgreSQL (via Docker or Neon)
3. **JWT Token**: From Better Auth frontend (for authenticated endpoints)

## Quick Start

### 1. Test Health Endpoints (No Auth)

```bash
# Root health check
curl http://localhost:8000/

# Health endpoint
curl http://localhost:8000/health
```

### 2. Get JWT Token

You need a JWT token from Better Auth for authenticated endpoints:

**Option A: Use Frontend** (Recommended)
1. Start frontend: `cd frontend && npm run dev`
2. Sign up / Log in at http://localhost:3000
3. Open browser dev tools → Application → Cookies
4. Copy the JWT token value
5. Export it: `export TOKEN='your_jwt_token'`

**Option B: Generate Test Token** (For development only)
```python
# In Python shell
from jose import jwt
import datetime

payload = {
    "sub": "550e8400-e29b-41d4-a716-446655440000",  # User UUID
    "email": "test@example.com",
    "iat": datetime.datetime.utcnow(),
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
}

token = jwt.encode(payload, "your-secret-key", algorithm="HS256")
print(token)
```

### 3. Test Authenticated Endpoints

```bash
# Set token
export TOKEN="your_jwt_token_here"

# List tasks (empty initially)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'

# Get task by ID
TASK_ID="550e8400-e29b-41d4-a716-446655440000"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks/$TASK_ID

# Update task
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries and snacks"}'

# Mark complete
curl -X PATCH http://localhost:8000/api/tasks/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN"

# Delete task
curl -X DELETE http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Automated Test Script

Run the comprehensive test script:

```bash
# Make script executable
chmod +x test_api.sh

# Set token and run
export TOKEN="your_jwt_token"
./test_api.sh
```

The script tests:
- ✅ Health check endpoints
- ✅ List tasks (empty)
- ✅ Create task
- ✅ Get task by ID
- ✅ Update task
- ✅ Mark task complete
- ✅ Delete task
- ✅ Validation errors (empty title, invalid status)

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

### Swagger UI (Recommended)
http://localhost:8000/docs

Features:
- Try endpoints directly in browser
- Automatic request/response examples
- Built-in authentication
- Schema validation

**Using Swagger UI:**
1. Open http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Enter: `Bearer your_jwt_token`
4. Click "Authorize"
5. Try any endpoint!

### ReDoc
http://localhost:8000/redoc

Features:
- Clean, readable documentation
- Better for sharing with stakeholders
- No interactive testing

### OpenAPI JSON
http://localhost:8000/openapi.json

- Machine-readable API spec
- Import into Postman, Insomnia, etc.

## Testing with Postman

1. Import OpenAPI spec:
   - Open Postman
   - Import → Link → `http://localhost:8000/openapi.json`

2. Set up environment:
   - Create new environment "Todo Dev"
   - Add variable: `token` = `your_jwt_token`

3. Configure requests:
   - Authorization → Type: Bearer Token
   - Token: `{{token}}`

## Testing with HTTPie

HTTPie is a user-friendly HTTP client:

```bash
# Install
pip install httpie

# List tasks
http GET localhost:8000/api/tasks "Authorization: Bearer $TOKEN"

# Create task
http POST localhost:8000/api/tasks \
  "Authorization: Bearer $TOKEN" \
  title="Buy groceries" description="Milk, eggs"

# Update task
http PUT localhost:8000/api/tasks/$TASK_ID \
  "Authorization: Bearer $TOKEN" \
  title="Updated title"

# Delete task
http DELETE localhost:8000/api/tasks/$TASK_ID \
  "Authorization: Bearer $TOKEN"
```

## Validation Testing

### Valid Inputs

```bash
# Minimal valid task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Task"}'

# Complete valid task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

### Invalid Inputs (Should return 422)

```bash
# Empty title
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "   ", "description": "Test"}'

# Missing title
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Test"}'

# Title too long
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"$(python -c 'print("x" * 256)')\"}"

# Description too long
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Test\", \"description\": \"$(python -c 'print("x" * 1001)')\"}"

# Invalid status
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in-progress"}'
```

## Authentication Testing

### Valid Token
```bash
# Should return 200 OK
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
```

### Missing Token
```bash
# Should return 401 Unauthorized
curl http://localhost:8000/api/tasks
```

### Invalid Token
```bash
# Should return 401 Unauthorized
curl -H "Authorization: Bearer invalid_token" http://localhost:8000/api/tasks
```

### Expired Token
```bash
# Should return 401 Unauthorized
export EXPIRED_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired"
curl -H "Authorization: Bearer $EXPIRED_TOKEN" http://localhost:8000/api/tasks
```

## Data Isolation Testing

To verify user data isolation:

1. Create tasks with User A's token
2. Try to access with User B's token (should get 404 or empty list)
3. Verify User B cannot see User A's tasks

```bash
# User A creates task
export TOKEN_A="user_a_token"
TASK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title": "User A Task"}')

TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')

# User B tries to access (should fail)
export TOKEN_B="user_b_token"
curl -H "Authorization: Bearer $TOKEN_B" \
  http://localhost:8000/api/tasks/$TASK_ID
# Should return: 404 Not Found
```

## Expected HTTP Status Codes

| Endpoint | Method | Success | Errors |
|----------|--------|---------|--------|
| `/api/tasks` | GET | 200 | 401 |
| `/api/tasks/{id}` | GET | 200 | 401, 404 |
| `/api/tasks` | POST | 201 | 401, 422 |
| `/api/tasks/{id}` | PUT | 200 | 401, 404, 422 |
| `/api/tasks/{id}` | DELETE | 204 | 401, 404 |
| `/api/tasks/{id}/complete` | PATCH | 200 | 401, 404 |

## Troubleshooting

### Issue: "Invalid or expired token"
**Solution**:
- Verify token is not expired
- Check BETTER_AUTH_SECRET matches frontend
- Ensure token format is correct (no extra quotes/spaces)

### Issue: "Task not found" (but task exists)
**Solution**:
- Verify you're using the correct user's token
- Task might belong to different user
- Check task_id is correct UUID format

### Issue: "Title cannot be empty"
**Solution**:
- Ensure title has non-whitespace characters
- Title must be 1-255 characters after trimming

### Issue: Connection refused
**Solution**:
- Verify backend is running: `uvicorn app.main:app --reload`
- Check port 8000 is available
- Verify DATABASE_URL is correct

### Issue: Database errors
**Solution**:
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Run migrations if needed
- Verify tables exist: `psql -U user -d todo_db -c "\dt"`

## Performance Testing

Basic load testing with Apache Bench:

```bash
# Install ab (Apache Bench)
# Ubuntu/Debian: apt-get install apache2-utils
# macOS: already included

# Test list endpoint
ab -n 1000 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks
```

For more advanced testing, use:
- **Locust**: Python-based load testing
- **k6**: Modern load testing tool
- **Artillery**: Node.js load testing

## Automated Testing (Future)

Backend includes pytest test suite (to be implemented):

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_tasks.py::test_create_task
```

## Next Steps

1. ✅ Test all endpoints manually
2. ✅ Verify authentication works
3. ✅ Check validation errors
4. ✅ Test data isolation
5. ⏳ Write automated tests (pytest)
6. ⏳ Set up CI/CD pipeline
7. ⏳ Add integration tests with frontend

## Resources

- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Pytest Documentation**: https://docs.pytest.org/
- **HTTPie**: https://httpie.io/
- **Postman**: https://www.postman.com/
- **curl Tutorial**: https://curl.se/docs/manual.html
