# API Specifications

This directory contains API-related specifications for the Evolution of Todo application.

## Files

### `endpoints.md`
Complete REST API endpoint documentation including:
- All task management endpoints (List, Get, Create, Update, Delete, Complete)
- Authentication requirements (JWT Bearer tokens)
- Request/response schemas
- HTTP status codes
- Error response formats
- Data isolation enforcement
- cURL examples and testing guides
- Interactive documentation links

### `validation.md`
Input validation rules for Phase II:
- Title validation (1-255 chars, non-empty)
- Description validation (max 1000 chars)
- Status validation (pending/completed)
- Pydantic schema implementations
- Error messages and test cases

## Quick Reference

### Base URL
```
http://localhost:8000
```

### Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Health check | No |
| GET | `/health` | Health check | No |
| GET | `/api/tasks` | List all user's tasks | Yes |
| GET | `/api/tasks/{id}` | Get specific task | Yes |
| POST | `/api/tasks` | Create new task | Yes |
| PUT | `/api/tasks/{id}` | Update task | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |
| PATCH | `/api/tasks/{id}/complete` | Mark task complete | Yes |

### Authentication

All `/api/*` endpoints require JWT Bearer token:
```
Authorization: Bearer <jwt_token>
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Implementation Status

Phase II (Current):
- ✅ Endpoints specification complete
- ✅ Validation rules defined
- ⏳ Backend implementation in progress
- ⏳ Frontend integration pending

## Testing

### Manual Testing
```bash
# Set token
export TOKEN="your_jwt_token_here"

# List tasks
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing"}'
```

### Automated Testing
See `backend/tests/` for test suite (to be implemented).

## Related Specifications

- **Database Schema**: `../database/schema.md`
- **Architecture**: `../architecture.md`
- **Enhanced Validation** (Future): `../future-phases/validation-enhanced.md`

## Notes

- All endpoints enforce user-based data isolation
- No pagination in Phase II (add in Phase III)
- No rate limiting in Phase II
- CORS configured for localhost:3000 (frontend)

---

Last updated: 2025-01-08
