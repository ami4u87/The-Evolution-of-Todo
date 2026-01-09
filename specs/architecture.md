# Architecture - Phase II Full-Stack Todo Application

## System Architecture

### High-Level Overview
```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────┐
│   Next.js Frontend          │
│   - App Router              │
│   - Better Auth Client      │
│   - JWT Token Management    │
└────────┬────────────────────┘
         │ REST API (JWT Bearer Token)
         ▼
┌─────────────────────────────┐
│   FastAPI Backend           │
│   - JWT Verification        │
│   - Business Logic          │
│   - SQLModel ORM            │
└────────┬────────────────────┘
         │ SQL
         ▼
┌─────────────────────────────┐
│   Neon PostgreSQL           │
│   - Users Table             │
│   - Tasks Table             │
└─────────────────────────────┘
```

## Component Architecture

### Frontend (/frontend)
- **Framework**: Next.js 16+ with App Router
- **Authentication**: Better Auth for user management and JWT token generation
- **State Management**: React hooks and server components
- **API Communication**: Fetch API with JWT bearer tokens

### Backend (/backend)
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Authentication**: JWT token verification (shared secret with frontend)
- **Authorization**: User-based data filtering (all queries include user_id)
- **Validation**: Pydantic models

### Database
- **Provider**: Neon Serverless PostgreSQL
- **Schema**:
  - `users` table: id, email, password_hash, created_at
  - `tasks` table: id, user_id, title, description, status, created_at, updated_at
  - Foreign key: tasks.user_id → users.id

## Authentication Flow
1. User signs up/logs in via Better Auth on frontend
2. Better Auth generates JWT token with user claims
3. Frontend stores JWT token (httpOnly cookie or secure storage)
4. Frontend includes JWT in Authorization header for all API requests
5. Backend verifies JWT signature using shared BETTER_AUTH_SECRET
6. Backend extracts user_id from JWT claims
7. Backend filters all data operations by authenticated user_id

## API Design
- Base URL: `/api/tasks`
- All endpoints require `Authorization: Bearer <jwt_token>` header
- User isolation enforced at database query level

### Endpoints
- `GET /api/tasks` - List all tasks for authenticated user
- `POST /api/tasks` - Create new task for authenticated user
- `GET /api/tasks/{task_id}` - Get specific task (if owned by user)
- `PUT /api/tasks/{task_id}` - Update task (if owned by user)
- `DELETE /api/tasks/{task_id}` - Delete task (if owned by user)
- `PATCH /api/tasks/{task_id}/complete` - Mark task complete (if owned by user)

## Security Considerations
- JWT tokens for stateless authentication
- Shared secret between frontend and backend (BETTER_AUTH_SECRET)
- Row-level security: All queries filtered by user_id
- HTTPS only in production
- Environment variables for secrets
- Input validation via Pydantic models

## Development Environment
- Docker Compose orchestrates:
  - Frontend dev server (localhost:3000)
  - Backend dev server (localhost:8000)
  - PostgreSQL database (localhost:5432) or Neon connection

## Data Isolation
- Every task belongs to exactly one user (user_id foreign key)
- All API endpoints verify JWT and extract user_id
- Database queries automatically filter by authenticated user_id
- No user can access another user's tasks

## Future Architecture Considerations
- Horizontal scaling of backend services
- Caching layer (Redis) for frequently accessed data
- Real-time updates via WebSockets
- AI integration for smart task management
- Cloud deployment (Vercel for frontend, cloud run/lambda for backend)
