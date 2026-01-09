# API Quick Reference Card

## Base URL
```
http://localhost:8000
```

## Authentication
```
Authorization: Bearer <jwt_token>
```

---

## Endpoints

### List Tasks
```bash
GET /api/tasks
→ 200 OK: Task[]
```

### Get Task
```bash
GET /api/tasks/{id}
→ 200 OK: Task
→ 404: Not found
```

### Create Task
```bash
POST /api/tasks
Content-Type: application/json

{
  "title": "string (required, 1-255)",
  "description": "string (optional, max 1000)"
}

→ 201 Created: Task
→ 422: Validation error
```

### Update Task
```bash
PUT /api/tasks/{id}
Content-Type: application/json

{
  "title": "string (optional, 1-255)",
  "description": "string (optional, max 1000)",
  "status": "pending|completed (optional)"
}

→ 200 OK: Task
→ 404: Not found
→ 422: Validation error
```

### Delete Task
```bash
DELETE /api/tasks/{id}
→ 204 No Content
→ 404: Not found
```

### Mark Complete
```bash
PATCH /api/tasks/{id}/complete
→ 200 OK: Task
→ 404: Not found
```

---

## Response Schema

### Task Object
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string | null",
  "status": "pending | completed",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 401 | Unauthorized (invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Error Format

### Single Error
```json
{
  "detail": "Error message"
}
```

### Validation Errors
```json
{
  "detail": [
    {
      "field": "title",
      "message": "Title is required"
    }
  ]
}
```

---

## Validation Rules

### Title
- Required
- 1-255 characters
- Cannot be empty or whitespace-only

### Description
- Optional
- Max 1000 characters

### Status
- Must be "pending" or "completed"

---

## cURL Examples

### Setup
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export API="http://localhost:8000/api"
```

### List
```bash
curl -H "Authorization: Bearer $TOKEN" $API/tasks
```

### Create
```bash
curl -X POST $API/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"2 gallons"}'
```

### Update
```bash
curl -X PUT $API/tasks/{id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk and eggs"}'
```

### Complete
```bash
curl -X PATCH $API/tasks/{id}/complete \
  -H "Authorization: Bearer $TOKEN"
```

### Delete
```bash
curl -X DELETE $API/tasks/{id} \
  -H "Authorization: Bearer $TOKEN"
```

---

## Interactive Docs
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Security Notes
- ✓ All endpoints require JWT authentication
- ✓ User can only access their own tasks
- ✓ Task ownership verified on all operations
- ✓ 404 returned for non-existent or unauthorized tasks (prevents info leakage)
