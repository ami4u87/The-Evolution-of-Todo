# Quick Start - Get Running in 5 Minutes

## Prerequisites Check
```bash
python --version  # Should be 3.12+
node --version    # Should be 18+
npm --version
docker --version  # Optional but recommended
```

---

## Step 1: Database (30 seconds)

### Option A: Docker (Easiest)
```bash
docker-compose up postgres -d
```

### Option B: Local PostgreSQL
```bash
createdb todo_db
```

**✅ Verify**: Database is running

---

## Step 2: Backend (2 minutes)

```bash
cd backend

# Install dependencies
pip install uv
uv pip install -e .

# Environment already configured (.env file created)

# Generate test token
python generate_test_token.py

# Copy and save the token that's printed!
# Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Verify**: Open http://localhost:8000/docs

---

## Step 3: Frontend (2 minutes)

**Open NEW terminal:**

```bash
cd frontend

# Install dependencies
npm install

# Environment already configured (.env.local.example exists)
cp .env.local.example .env.local

# Start server
npm run dev
```

**✅ Verify**: Open http://localhost:3000

---

## Step 4: Test It! (30 seconds)

1. Visit http://localhost:3000
2. Click "Sign In"
3. Paste the JWT token from Step 2
4. Click "Sign in"
5. You're in the dashboard!
6. Create a task:
   - Title: "Test Task"
   - Description: "Testing the app"
   - Click "Create Task"
7. ✅ Task appears in the list!

---

## Quick Test Commands

**Backend API** (in new terminal):
```bash
export TOKEN="your-token-here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
```

**Create task via API**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "API Test", "description": "Created via curl"}'
```

---

## Troubleshooting

### Backend: "ModuleNotFoundError"
```bash
cd backend
uv pip install -e .
```

### Frontend: "Cannot find module"
```bash
cd frontend
npm install
```

### Database: "Connection refused"
```bash
docker-compose up postgres -d
# or restart local PostgreSQL
```

### Token: "Invalid or expired token"
```bash
cd backend
python generate_test_token.py
# Use the new token
```

---

## What's Running?

- **Backend**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Database**: localhost:5432

---

## Stop Everything

```bash
# Stop backend: Ctrl+C in backend terminal
# Stop frontend: Ctrl+C in frontend terminal
# Stop database: docker-compose down
```

---

## Next Steps

- Read `TESTING-E2E.md` for comprehensive testing
- Check `PHASE-II-COMPLETE.md` for full documentation
- Review `backend/IMPLEMENTATION.md` and `frontend/FRONTEND_README.md`

---

**Got issues?** Check the troubleshooting section or see `TESTING-E2E.md` for detailed solutions.
