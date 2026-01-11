# End-to-End Testing Guide - Full Stack Todo Application

## Overview
This guide will walk you through testing the complete Todo application from database setup to frontend UI interactions.

**Estimated Time**: 30-45 minutes
**Prerequisites**: Python 3.12+, Node.js 18+, PostgreSQL or Docker

---

## Pre-Test Checklist

Before starting, ensure you have:
- [ ] Python 3.12+ installed: `python --version`
- [ ] Node.js 18+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] Docker installed (optional): `docker --version`
- [ ] Git repository cloned
- [ ] Terminal/command prompt open

---

## Phase 1: Database Setup

### Option A: Docker Compose (Recommended)

```bash
# From project root
docker-compose up postgres -d

# Verify database is running
docker ps | grep postgres

# Expected output: Container named "todo-postgres" running on port 5432
```

### Option B: Local PostgreSQL

```bash
# Create database
createdb todo_db

# Or with psql
psql -U postgres -c "CREATE DATABASE todo_db;"

# Verify
psql -U postgres -l | grep todo_db
```

**✅ Checkpoint**: Database is running and accessible

---

## Phase 2: Backend Setup

### Step 1: Install Dependencies

```bash
cd backend

# Install UV package manager (if not installed)
pip install uv

# Install backend dependencies
uv pip install -e .

# Verify installation
python -c "import fastapi; import sqlmodel; import jose; print('✅ All imports successful')"
```

**Expected Output**: `✅ All imports successful`

### Step 2: Configure Environment

Backend `.env` file should already be created. Verify:

```bash
cat .env
```

**Expected Content**:
```
DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db
BETTER_AUTH_SECRET=test-secret-key-for-development-minimum-32-characters-long
API_PREFIX=/api
DEBUG=true
CORS_ORIGINS=http://localhost:3000
```

### Step 3: Generate Test JWT Token

```bash
python generate_test_token.py
```

**Expected Output**:
```
================================================================================
TEST JWT TOKEN GENERATED
================================================================================

User ID: 550e8400-e29b-41d4-a716-446655440000
Email: test@example.com
Expires: [date]

TOKEN:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

================================================================================
USAGE:
================================================================================
...
```

**🔑 SAVE THIS TOKEN** - You'll need it for testing!

```bash
# Export token for API testing
export TOKEN="your_generated_token_here"
```

### Step 4: Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Checkpoint**: Backend running on http://localhost:8000

---

## Phase 3: Backend API Testing

**Open a NEW terminal** (keep backend running in the first terminal)

### Test 1: Health Check (No Auth)

```bash
curl http://localhost:8000/
```

**Expected Response**:
```json
{
  "status": "healthy",
  "message": "Todo API - Phase II",
  "version": "2.0.0"
}
```

**✅ Pass Criteria**: HTTP 200, correct JSON response

### Test 2: Interactive Documentation

Open browser: http://localhost:8000/docs

**Expected**: Swagger UI with all endpoints listed

**✅ Pass Criteria**:
- Page loads successfully
- 8 endpoints visible (/, /health, 6 task endpoints)
- "Authorize" button visible

### Test 3: List Tasks (Empty - Auth Required)

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
```

**Expected Response**:
```json
[]
```

**✅ Pass Criteria**: HTTP 200, empty array (no tasks yet)

### Test 4: Create Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task 1",
    "description": "This is a test task created via API"
  }'
```

**Expected Response**:
```json
{
  "id": "uuid-here",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Test Task 1",
  "description": "This is a test task created via API",
  "status": "pending",
  "created_at": "2025-01-08T...",
  "updated_at": "2025-01-08T..."
}
```

**✅ Pass Criteria**:
- HTTP 201 Created
- Task has UUID id
- user_id matches token
- status is "pending"

**💾 SAVE THE TASK ID** from the response:
```bash
export TASK_ID="paste-task-id-here"
```

### Test 5: List Tasks (Should show 1 task)

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
```

**Expected Response**: Array with 1 task

**✅ Pass Criteria**: HTTP 200, array length = 1

### Test 6: Get Specific Task

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks/$TASK_ID
```

**Expected Response**: Same task object as created

**✅ Pass Criteria**: HTTP 200, task details match

### Test 7: Update Task

```bash
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task 1 - Updated",
    "description": "Updated description"
  }'
```

**Expected Response**: Task with updated title and description, `updated_at` refreshed

**✅ Pass Criteria**: HTTP 200, title and description updated

### Test 8: Mark Task Complete

```bash
curl -X PATCH http://localhost:8000/api/tasks/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**: Task with `status: "completed"`

**✅ Pass Criteria**: HTTP 200, status changed to "completed"

### Test 9: Create Second Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task 2",
    "description": null
  }'
```

**Expected Response**: New task with null description

**✅ Pass Criteria**: HTTP 201, null description accepted

**💾 SAVE SECOND TASK ID**:
```bash
export TASK_ID_2="paste-second-task-id-here"
```

### Test 10: List Tasks (Should show 2 tasks)

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
```

**Expected Response**: Array with 2 tasks (1 completed, 1 pending)

**✅ Pass Criteria**: HTTP 200, array length = 2

### Test 11: Delete Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/$TASK_ID_2 \
  -H "Authorization: Bearer $TOKEN" -w "\nHTTP Status: %{http_code}\n"
```

**Expected Response**: Empty body, HTTP 204

**✅ Pass Criteria**: HTTP 204 No Content

### Test 12: Verify Deletion

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks/$TASK_ID_2 \
  -w "\nHTTP Status: %{http_code}\n"
```

**Expected Response**: HTTP 404 Not Found

**✅ Pass Criteria**: Task no longer exists

### Test 13: Validation - Empty Title (Should Fail)

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "   ",
    "description": "Test"
  }' \
  -w "\nHTTP Status: %{http_code}\n"
```

**Expected Response**: HTTP 422 Unprocessable Entity

**✅ Pass Criteria**: HTTP 422, error message about empty title

### Test 14: Validation - Invalid Status (Should Fail)

```bash
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in-progress"
  }' \
  -w "\nHTTP Status: %{http_code}\n"
```

**Expected Response**: HTTP 422 Unprocessable Entity

**✅ Pass Criteria**: HTTP 422, error about invalid status

### Test 15: Authentication - Missing Token (Should Fail)

```bash
curl http://localhost:8000/api/tasks -w "\nHTTP Status: %{http_code}\n"
```

**Expected Response**: HTTP 401 Unauthorized

**✅ Pass Criteria**: HTTP 401, error about missing authentication

---

## Phase 4: Frontend Setup

**Open a NEW terminal** (keep backend running)

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

**Expected Output**: Dependencies installed successfully, no errors

### Step 2: Configure Environment

Frontend `.env.local.example` should exist. Create `.env.local`:

```bash
cp .env.local.example .env.local
```

Verify content:
```bash
cat .env.local
```

**Expected Content**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3: Start Frontend Development Server

```bash
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 16.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Starting...
 ✓ Ready in Xs
```

**✅ Checkpoint**: Frontend running on http://localhost:3000

---

## Phase 5: Frontend UI Testing

### Test 1: Home Page

1. Open browser: http://localhost:3000
2. Verify page loads with hero section
3. Check "Get Started" and "Sign In" buttons visible
4. Verify features section displays (3 cards)
5. Check tech stack section shows (Next.js, FastAPI, PostgreSQL, TypeScript)

**✅ Pass Criteria**:
- Page loads without errors
- All sections visible
- Responsive design works

### Test 2: Login Page

1. Click "Sign In" or go to http://localhost:3000/login
2. Verify JWT token textarea is visible
3. Paste the token you generated earlier
4. Click "Sign in"
5. Should redirect to /dashboard

**✅ Pass Criteria**:
- Login page loads
- Token textarea accepts input
- Redirect to dashboard on submit

### Test 3: Dashboard - Initial Load

1. Verify dashboard loads at http://localhost:3000/dashboard
2. Check task form visible on left
3. Check "My Tasks" header visible
4. Check "Logout" button visible
5. Verify task list shows (with the 1 task from API testing)

**✅ Pass Criteria**:
- Dashboard loads successfully
- Existing task(s) from API tests displayed
- Layout correct (form left, list right on desktop)

### Test 4: Create Task via UI

1. In the task form, enter:
   - Title: "Buy groceries"
   - Description: "Milk, eggs, bread, butter"
2. Click "Create Task"
3. Verify task appears in the list immediately
4. Check task shows as "pending" status

**✅ Pass Criteria**:
- Form submits successfully
- New task appears in "Pending Tasks" section
- Form resets after submission
- No errors displayed

### Test 5: Toggle Task Completion

1. Find the task you just created
2. Click the checkbox next to "Buy groceries"
3. Verify task moves to "Completed Tasks" section
4. Check task has green background and strikethrough text
5. Click checkbox again
6. Verify task moves back to "Pending Tasks"

**✅ Pass Criteria**:
- Checkbox toggles task status
- Task moves between sections
- Visual styling updates correctly
- No page reload required

### Test 6: Edit Task

1. Find any pending task
2. Click "Edit" button
3. Verify inline edit mode appears
4. Change title to "Buy groceries and snacks"
5. Change description to "Updated description"
6. Click "Save"
7. Verify changes appear immediately

**✅ Pass Criteria**:
- Edit mode activates
- Changes save successfully
- Inline editing works without full page reload
- Cancel button works to discard changes

### Test 7: Delete Task

1. Find any task
2. Click "Delete" button
3. Verify confirmation dialog appears
4. Click "OK" to confirm
5. Verify task disappears from list immediately

**✅ Pass Criteria**:
- Confirmation dialog shows
- Task deletes successfully
- UI updates immediately
- No errors

### Test 8: Task Count Badges

1. Create multiple tasks (mix of pending and completed)
2. Verify badges show correct counts:
   - "X Pending"
   - "Y Completed"
   - "Z Total"
3. Toggle a task status
4. Verify badges update immediately

**✅ Pass Criteria**:
- Badges display correct counts
- Counts update in real-time
- No discrepancies

### Test 9: Form Validation

1. Try to create task with empty title
2. Verify error message displays
3. Try to create task with very long title (256+ characters)
4. Verify character counter shows limit
5. Try to create task with very long description (1001+ characters)
6. Verify character counter shows limit

**✅ Pass Criteria**:
- Empty title prevented
- Character counters work
- Validation messages clear
- Form doesn't submit invalid data

### Test 10: Empty State

1. Delete all tasks (or use clean database)
2. Verify empty state displays:
   - Icon visible
   - "No tasks yet" message
   - Helpful text about creating first task

**✅ Pass Criteria**:
- Empty state shows when no tasks
- Messaging is clear and helpful
- Icon displays correctly

### Test 11: Loading States

1. Open browser DevTools → Network tab
2. Throttle network to "Slow 3G"
3. Refresh dashboard
4. Verify loading spinner appears while fetching tasks
5. Try creating a task
6. Verify button shows "Creating..." during submission

**✅ Pass Criteria**:
- Loading indicators appear during async operations
- UI is disabled during loading
- No confusing states

### Test 12: Error Handling

1. Stop the backend server (Ctrl+C in backend terminal)
2. Try to create a task in the UI
3. Verify error message displays
4. Start backend again
5. Verify retry works

**✅ Pass Criteria**:
- Error messages are user-friendly
- No cryptic technical errors exposed
- Retry mechanism works

### Test 13: Logout

1. Click "Logout" button in dashboard
2. Verify redirect to home page
3. Try to access http://localhost:3000/dashboard
4. Verify redirect back to login (401 handling)

**✅ Pass Criteria**:
- Logout clears authentication
- Protected routes redirect to login
- Home page accessible after logout

### Test 14: Responsive Design

1. Resize browser to mobile width (375px)
2. Verify layout adjusts:
   - Task form stacks on top
   - Task list below form
   - Buttons remain accessible
3. Resize to tablet (768px)
4. Verify intermediate layout
5. Resize to desktop (1024px+)
6. Verify side-by-side layout

**✅ Pass Criteria**:
- All breakpoints work correctly
- Content remains accessible at all sizes
- No horizontal scrolling
- Touch targets adequate on mobile

---

## Phase 6: Data Isolation Testing

### Test User Isolation

1. Generate a SECOND test token with different user_id:

```python
# In Python
from jose import jwt
from datetime import datetime, timedelta

payload = {
    "sub": "660e8400-e29b-41d4-a716-446655440001",  # Different user
    "email": "user2@example.com",
    "exp": datetime.utcnow() + timedelta(days=7)
}

token2 = jwt.encode(payload, "test-secret-key-for-development-minimum-32-characters-long", algorithm="HS256")
print(token2)
```

2. In backend terminal, test with first user's token:
```bash
export TOKEN1="first-user-token"
curl -H "Authorization: Bearer $TOKEN1" http://localhost:8000/api/tasks
```

3. Note the tasks returned

4. Test with second user's token:
```bash
export TOKEN2="second-user-token"
curl -H "Authorization: Bearer $TOKEN2" http://localhost:8000/api/tasks
```

5. Verify EMPTY array returned (no tasks for new user)

6. Create a task with second user:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"title": "User 2 Task"}'
```

7. Try to access User 2's task with User 1's token:
```bash
export USER2_TASK_ID="task-id-from-step-6"
curl -H "Authorization: Bearer $TOKEN1" \
  http://localhost:8000/api/tasks/$USER2_TASK_ID \
  -w "\nHTTP Status: %{http_code}\n"
```

**✅ Pass Criteria**:
- User 1 cannot see User 2's tasks
- User 2 cannot see User 1's tasks
- Attempting to access another user's task returns 404
- Each user has isolated task list

---

## Phase 7: Database Verification

```bash
# Connect to database
psql postgresql://todo_user:todo_password@localhost:5432/todo_db

# Or if using Docker
docker exec -it todo-postgres psql -U todo_user -d todo_db
```

### Verify Tables

```sql
\dt
```

**Expected Output**: Tables `users`, `tasks`

### Check Tasks

```sql
SELECT id, user_id, title, status, created_at FROM tasks;
```

**✅ Pass Criteria**: Tasks match what you created in UI/API

### Check User Isolation in Database

```sql
SELECT user_id, COUNT(*) as task_count
FROM tasks
GROUP BY user_id;
```

**✅ Pass Criteria**: Each user_id has their own task count

### Verify Foreign Keys

```sql
\d tasks
```

**✅ Pass Criteria**: Foreign key constraint on user_id references users(id)

---

## Test Results Checklist

### Backend API (15 tests)
- [ ] Health check works
- [ ] Interactive docs accessible
- [ ] List tasks (empty) - 401 without token
- [ ] Create task works
- [ ] List tasks shows created task
- [ ] Get specific task works
- [ ] Update task works
- [ ] Mark complete works
- [ ] Create second task works
- [ ] List shows multiple tasks
- [ ] Delete task works
- [ ] Verify deletion (404)
- [ ] Validation - empty title fails
- [ ] Validation - invalid status fails
- [ ] Authentication - missing token fails

### Frontend UI (14 tests)
- [ ] Home page loads correctly
- [ ] Login page works
- [ ] Dashboard loads with tasks
- [ ] Create task via UI works
- [ ] Toggle completion works
- [ ] Edit task works
- [ ] Delete task works
- [ ] Task count badges correct
- [ ] Form validation works
- [ ] Empty state displays
- [ ] Loading states show
- [ ] Error handling works
- [ ] Logout works
- [ ] Responsive design works

### Integration (1 test)
- [ ] Data isolation verified (users can't see each other's tasks)

---

## Expected Results Summary

**Total Tests**: 30
**Expected Passes**: 30
**Expected Failures**: 0

---

## Troubleshooting

### Backend won't start
**Issue**: `ModuleNotFoundError` or import errors
**Solution**:
```bash
cd backend
uv pip install -e .
```

### Database connection error
**Issue**: `could not connect to server`
**Solution**:
```bash
# Check if PostgreSQL is running
docker ps
# or
pg_isready
```

### Frontend won't start
**Issue**: `Cannot find module` errors
**Solution**:
```bash
cd frontend
rm -rf node_modules .next
npm install
```

### CORS errors in browser
**Issue**: `Access-Control-Allow-Origin` errors
**Solution**: Verify backend `.env` has:
```
CORS_ORIGINS=http://localhost:3000
```

### 401 Unauthorized
**Issue**: All API calls return 401
**Solution**:
- Verify token is correct
- Check BETTER_AUTH_SECRET matches in both backend/.env
- Regenerate token if expired

---

## Performance Benchmarks

### Expected Response Times (Local Development)
- Health check: < 10ms
- List tasks: < 50ms
- Create task: < 100ms
- Update task: < 100ms
- Delete task: < 50ms

### Frontend Metrics
- Initial page load: < 2s
- Task list render: < 100ms
- Form submission: < 500ms (including API call)

---

## Success Criteria

✅ **Backend**: All 15 API tests pass
✅ **Frontend**: All 14 UI tests pass
✅ **Integration**: Data isolation verified
✅ **Database**: Schema correct, data persists
✅ **Security**: Authentication enforced, users isolated
✅ **UX**: Responsive, loading states, error handling

---

## Post-Testing

After successful testing:

1. **Document Results**: Fill out Test Results Checklist above
2. **Take Screenshots**: Capture dashboard with tasks
3. **Note Issues**: Document any bugs or unexpected behavior
4. **Clean Up**:
   ```bash
   # Stop services
   # Backend: Ctrl+C
   # Frontend: Ctrl+C
   # Database: docker-compose down
   ```

---

## Next Steps After Testing

1. **Fix Issues**: Address any failing tests
2. **Add Better Auth**: Replace temporary login
3. **Write Automated Tests**: pytest for backend, Jest for frontend
4. **Deploy**: Deploy to production environment
5. **Phase III**: Implement enhanced features

---

## Quick Test Script

For rapid testing, use the automated test script:

```bash
cd backend
chmod +x test_api.sh
export TOKEN="your-token"
./test_api.sh
```

This runs all 15 backend API tests automatically.

---

**Testing completed?** Proceed to `DEPLOYMENT.md` for production deployment guide.
