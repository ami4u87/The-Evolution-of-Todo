# The Evolution of Todo - AI-Powered Task Management (Phase III)

A full-stack todo application with AI-powered chat interface for natural language task management. This is Phase III of a multi-phase project that evolved from a console application to a web-based system with AI assistance.

## Features

✅ **AI-Powered Chat Interface** (NEW in Phase III):
- Natural language task management
- Chat with AI assistant to create, update, delete, and complete tasks
- Commands like "Add task: Buy milk", "List my tasks", "Mark grocery task as done"
- Intelligent task search and matching
- Real-time tool execution feedback

✅ **Full CRUD Operations**:
- Create new todo items with title and optional description
- List all todos with status and timestamps
- Mark todos as completed (track progress)
- Update todo details (title and/or description)
- Delete todos permanently with confirmation

✅ **User Authentication**:
- Email/password registration with validation
- Secure login with JWT token authentication
- Password strength requirements (uppercase, lowercase, digit, special character)
- Email format validation
- Password confirmation field
- Duplicate email prevention
- Auto-login after signup

✅ **Multi-User Support**:
- User-specific data isolation
- Secure session management
- Individual task ownership

✅ **Full-Stack Architecture**:
- Next.js 16+ frontend with App Router
- FastAPI backend with PostgreSQL database
- RESTful API with JWT authentication
- OpenAI integration for AI chat
- TypeScript strict mode
- Clean layer separation (frontend/backend)

## Prerequisites

- **Python 3.13+** (required for backend)
- **Node.js 18+** (required for frontend)
- **UV package manager** (recommended for backend environment setup)
- **npm or yarn** (for frontend dependencies)

Check your versions:
```bash
python --version  # Should show 3.13.x or higher
node --version    # Should show 18.x or higher
npm --version     # Should show recent version
```

## Quick Start

### Option 1: Full Stack Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Hacathorn-II-The-Evolution-of-Todo
   ```

2. **Setup Backend**:
   ```bash
   cd backend
   uv venv --python 3.13
   # Activate environment (Windows PowerShell):
   .\.venv\Scripts\Activate.ps1
   # Install dependencies:
   uv pip install -e .
   # Start backend server:
   uv run uvicorn app.main:app --reload
   ```

3. **Setup Frontend** (in new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Option 2: Using Standard Python venv

1. **Clone and navigate**:
   ```bash
   git clone <repository-url>
   cd Hacathorn-II-The-Evolution-of-Todo
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv .venv
   # Activate environment and install:
   # Windows: .venv\Scripts\activate
   # Unix/Mac: source .venv/bin/activate
   pip install -e .
   uvicorn app.main:app --reload
   ```

3. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Usage Guide

After starting both frontend and backend servers, access the application through your web browser:

1. **Open browser** and navigate to: http://localhost:3000
2. **Sign up** for a new account or **Log in** if you already have an account
3. **Dashboard** shows your personal todo list
4. **Create, update, delete** todos with full CRUD functionality
5. **AI Chat** - Click "AI Chat" button to access the conversational interface

### Authentication Flow

**Sign up for a new account**:
1. Navigate to http://localhost:3000/signup
2. Fill in email and password (must meet strength requirements)
3. Click "Sign Up"
4. Automatically logged in and redirected to dashboard

**Log in to existing account**:
1. Navigate to http://localhost:3000/login
2. Enter your email and password
3. Click "Log In"
4. Redirected to dashboard with your todos

**Manage your todos**:
- **Create**: Click "Add Todo" button and fill in details
- **Update**: Click on any todo to edit title or description
- **Complete**: Click checkbox to mark as completed
- **Delete**: Click trash icon to delete todo permanently
- **Filter**: Toggle between "All", "Active", and "Completed" views

### AI Chat Interface (Phase III)

Access the AI chat at http://localhost:3000/chat or click "AI Chat" from the dashboard.

**Example commands:**
```
"Add task: Buy groceries tomorrow"
"List my tasks"
"What tasks are pending?"
"Mark the grocery task as complete"
"Update the grocery task description to include milk and eggs"
"Delete all completed tasks"
"Search for tasks about meeting"
```

**How it works:**
1. Type your message in natural language
2. The AI understands your intent and executes the appropriate action
3. You'll see the actions taken (create, update, delete, etc.) in the response
4. Changes are reflected immediately in your dashboard

**Supported operations:**
- `list_tasks` - List all your tasks (with optional status filter)
- `create_task` - Create a new task
- `update_task` - Update an existing task's title, description, or status
- `delete_task` - Delete a task permanently
- `mark_complete` - Mark a task as completed
- `search_tasks` - Search tasks by title or description

## Project Structure

```
Hacathorn-II-The-Evolution-of-Todo/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # Application entry point
│   │   ├── config.py        # Settings configuration
│   │   ├── database.py      # Database connection
│   │   ├── models/          # SQLModel database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py      # User model
│   │   │   └── task.py      # Task model
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── task.py      # Task DTOs
│   │   │   └── auth.py      # Authentication DTOs
│   │   ├── routers/         # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py     # Task endpoints
│   │   │   └── auth.py      # Authentication endpoints
│   │   ├── services/        # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py   # Task operations
│   │   │   ├── auth_service.py   # Authentication operations
│   │   │   └── chat_service.py   # AI chat processing (Phase III)
│   │   └── auth/            # Authentication utilities
│   │       ├── __init__.py
│   │       ├── jwt.py       # JWT verification
│   │       └── password.py  # Password hashing
│   ├── pyproject.toml       # Dependencies and configuration
│   ├── .env                 # Environment variables (git-ignored)
│   └── README.md            # Backend-specific documentation
├── frontend/                # Next.js 16+ frontend application
│   ├── app/                 # App Router pages
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Landing page
│   │   ├── login/           # Authentication pages
│   │   │   └── page.tsx     # Login page
│   │   ├── signup/          # Sign up page
│   │   │   └── page.tsx     # Sign up page
│   │   ├── dashboard/       # Protected dashboard
│   │   │   └── page.tsx     # Task dashboard
│   │   └── chat/            # AI Chat interface (Phase III)
│   │       └── page.tsx     # Chat page
│   ├── components/          # React components
│   ├── lib/                 # Utilities and API client
│   │   ├── api-client.ts    # API communication
│   │   └── types.ts         # TypeScript types
│   ├── public/              # Static assets
│   ├── package.json         # Dependencies
│   ├── .env.local           # Environment variables
│   └── README.md            # Frontend-specific documentation
├── specs/                   # Specification documents
│   ├── features/            # Feature specifications
│   ├── api/                 # API endpoint specs
│   ├── database/            # Database schema specs
│   └── architecture.md      # System architecture
├── history/                 # Prompt History Records and ADRs
│   └── prompts/             # PHRs for learning and traceability
├── .env                     # Shared environment variables
├── docker-compose.yml       # Local development setup
├── README.md                # This file
└── CLAUDE.md                # Development guidelines
```

## Architecture

This application follows **strict layered architecture** across frontend and backend:

### Backend Architecture (FastAPI)
1. **Data Layer** (`backend/app/models/`):
   - SQLModel database models (User, Task)
   - SQLAlchemy ORM integration
   - PostgreSQL database schema

2. **Schema Layer** (`backend/app/schemas/`):
   - Pydantic request/response DTOs
   - Input validation and serialization
   - API contract definitions

3. **Business Logic Layer** (`backend/app/services/`):
   - Service classes with validation
   - Reusable business operations
   - Database transaction management

4. **API Layer** (`backend/app/routers/`):
   - FastAPI route handlers
   - Authentication middleware
   - Request/response processing

5. **Authentication Layer** (`backend/app/auth/`):
   - JWT token generation and verification
   - Password hashing utilities
   - User session management

### Frontend Architecture (Next.js 16+)
1. **Page Layer** (`frontend/app/`):
   - App Router pages
   - Server and Client components
   - Route-based navigation

2. **Component Layer** (`frontend/components/`):
   - Reusable UI components
   - Feature-specific components
   - Interactive elements

3. **Service Layer** (`frontend/lib/`):
   - API client with authentication
   - Type definitions and interfaces
   - Utility functions

## Key Features & Design Decisions

### Multi-User Support
- Individual user accounts with email/password authentication
- User-specific data isolation
- Secure session management with JWT tokens

### Authentication & Security
- Password strength validation (uppercase, lowercase, digit, special character)
- Secure password hashing with SHA-256 (temporary until bcrypt resolved)
- JWT token-based authentication
- Proper validation and error handling

### Database Integration
- PostgreSQL database with SQLModel
- User and Task relationship management
- Data persistence across sessions

### Frontend-Backend Communication
- RESTful API design
- CORS configuration for secure communication
- Proper error handling and user feedback

## Testing

### Backend Testing
- API endpoint validation
- Authentication flow testing
- Database integration tests
- Error condition verification

### Frontend Testing
- User interface validation
- Authentication flow testing
- API integration testing
- Cross-browser compatibility

## Technology Stack

**Backend:**
- FastAPI for web framework
- SQLModel for database ORM
- PostgreSQL for data storage
- JWT for authentication
- OpenAI SDK for AI chat (Phase III)
- Python 3.13+ for runtime

**Frontend:**
- Next.js 16+ with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Node.js for runtime

**Development:**
- UV for Python package management
- npm/yarn for JavaScript dependencies
- Git for version control

## Troubleshooting

### Backend Issues
- **Port already in use**: Change port in uvicorn command
- **Database connection**: Verify PostgreSQL is running
- **Authentication errors**: Check JWT secret in .env files
- **AI Chat not working**: Verify OPENAI_API_KEY is set in backend .env

### Frontend Issues
- **Cannot connect to backend**: Verify CORS settings and API URL
- **Environment variables**: Ensure NEXT_PUBLIC_API_URL is set correctly
- **Build errors**: Check TypeScript compilation errors

### Common Setup Issues
- **Python version**: Ensure Python 3.13+ is installed
- **Node version**: Ensure Node.js 18+ is installed
- **Dependency conflicts**: Clear node_modules and reinstall

## Documentation

- **Backend**: See `backend/README.md` for backend-specific details
- **Frontend**: See `frontend/README.md` for frontend-specific details
- **Architecture**: See `specs/architecture.md` for system design
- **API Spec**: See `specs/api/` for endpoint specifications
- **Database**: See `specs/database/` for schema definitions

## Migration from Phase I

The application evolved from a console-based single-user application to a full-stack multi-user web application while preserving business logic:

| Phase I (Console) | Phase II (Web) |
|-------------------|----------------|
| `src/services.py` | → `backend/app/services/` (preserved logic) |
| `src/models.py` | → `backend/app/models/` (enhanced with SQLModel) |
| `src/cli.py` | → `frontend/` (replaced with Next.js UI) |
| In-memory storage | → PostgreSQL database |
| Single-user | → Multi-user with authentication |

### Phase II → Phase III Changes

| Phase II | Phase III |
|----------|-----------|
| Manual CRUD via UI | + AI chat for natural language commands |
| Dashboard only | + `/chat` page with conversational interface |
| Basic task service | + Chat service with OpenAI integration |
| HTTP endpoints | + `/api/chat` endpoint with tool calling |

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your-shared-secret-key-min-32-chars
JWT_ALGORITHM=HS256
DEBUG=false
CORS_ORIGINS=http://localhost:3000

# Phase III - AI Chat
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o, gpt-3.5-turbo
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## License

[Specify license here]

## Contributing

[Specify contribution guidelines here]

## Support

For questions or issues:
1. Check backend and frontend README files for specific troubleshooting
2. Review architecture documentation in `specs/` directory
3. Open a GitHub issue with:
   - Python/Node.js versions
   - Operating system
   - Steps to reproduce
   - Error messages (full output)

---

**Phase III Complete** ✅

AI-powered chat interface added. Users can now manage tasks through natural language commands.
Full-stack application with authentication and AI assistance implemented.
