# In-Memory Todo Console Application (Phase I)

A command-line todo application built with Python 3.13+ that stores tasks entirely in memory. This is Phase I of a multi-phase project designed for clean evolution to web, database, and AI-enabled phases.

## Features

✅ **Full CRUD Operations**:
- Create new todo items with title and optional description
- List all todos with status and timestamps
- Mark todos as completed (track progress)
- Update todo details (title and/or description)
- Delete todos permanently with confirmation
- Graceful application exit (Ctrl+C or menu option)

✅ **User-Friendly**:
- Menu-driven interface (numbered options 1-6)
- Input validation with clear error messages
- No crashes on invalid input
- Confirmation prompts for destructive operations

✅ **Clean Code Architecture**:
- Strict layer separation (data/logic/UI)
- 100% docstring coverage with type hints
- Beginner-friendly, readable Python code
- Zero external dependencies (stdlib only)

## Prerequisites

- **Python 3.13+** (required)
- **UV package manager** (recommended for environment setup)

Check your Python version:
```bash
python --version  # Should show 3.13.x or higher
```

## Quick Start

### Option 1: Using UV (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Hacathorn-II-phase-1-console-app
   ```

2. **Create virtual environment**:
   ```bash
   uv venv --python 3.13
   ```

3. **Activate environment**:
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
   - Windows CMD: `.\.venv\Scripts\activate.bat`
   - macOS/Linux: `source .venv/bin/activate`

4. **Run the application**:
   ```bash
   python main.py
   ```

### Option 2: Using Standard Python venv

1. **Clone and navigate**:
   ```bash
   git clone <repository-url>
   cd Hacathorn-II-phase-1-console-app
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate and run** (same as Option 1 steps 3-4)

## Usage Guide

After launching with `python main.py`, you'll see the main menu:

```
=== Todo Application ===
1. Add Todo
2. List Todos
3. Mark Todo as Completed
4. Update Todo
5. Delete Todo
6. Exit
```

### Examples

**Create a todo**:
```
Choose option: 1
Enter todo title: Buy groceries
Enter description: Milk, eggs, bread
✓ Todo #1 created successfully!
```

**List todos**:
```
Choose option: 2

=== Your Todos ===
[1] Buy groceries (Pending)
    Created: 2026-01-02 10:30:15
    Description: Milk, eggs, bread
```

**Mark as completed**:
```
Choose option: 3
Enter todo ID: 1
✓ Todo #1 marked as completed!
```

**Exit**:
```
Choose option: 6
Goodbye! Your todos were in-memory only (all data lost).
```

## Project Structure

```
Hacathorn-II-phase-1-console-app/
├── src/
│   ├── __init__.py      # Package marker
│   ├── models.py        # TodoItem dataclass (data layer)
│   ├── store.py         # TodoStore class (storage layer)
│   ├── services.py      # Business logic (validation, CRUD)
│   └── cli.py           # CLI interface (user interaction)
├── main.py              # Application entry point
├── pyproject.toml       # UV project configuration
├── .python-version      # Python version (3.13+)
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── TESTING.md           # Manual testing checklist
└── specs/               # Design documents
    └── 001-todo-console-app/
        ├── spec.md           # Feature specification
        ├── plan.md           # Implementation plan
        ├── tasks.md          # Task breakdown
        ├── data-model.md     # Data structures
        ├── quickstart.md     # Detailed setup guide
        └── contracts/        # Function signatures
            └── services.md
```

## Architecture

This application follows **strict layered architecture** per the project constitution:

1. **Data Layer** (`src/models.py`):
   - TodoItem dataclass
   - Pure data structures, no logic

2. **Storage Layer** (`src/store.py`):
   - TodoStore class
   - In-memory CRUD operations
   - Auto-incrementing ID generation

3. **Business Logic Layer** (`src/services.py`):
   - Service functions with validation
   - NO I/O operations (no input()/print())
   - Reusable for future API endpoints

4. **UI Layer** (`src/cli.py`):
   - Menu-driven CLI interface
   - All user interaction (input/output)
   - NO business logic

## Key Features & Design Decisions

### In-Memory Only (Phase I Constraint)
- All todos stored in Python lists/dicts
- Data lost when application exits (by design)
- No file I/O, no database connections
- Session-scoped data lifetime

### Validation & Error Handling
- Title cannot be empty (validated before creation/update)
- ID validation (must exist in store)
- Type validation (graceful handling of non-numeric input)
- User-friendly error messages (no stack traces shown to user)

### ID Management
- Auto-incrementing IDs (start from 1)
- Monotonic counter (IDs never reused, even after deletion)
- Unbounded integers (no practical limit in Phase I)

### Status Management
- Default status: "pending"
- One-way transition: pending → completed
- No "uncomplete" in Phase I (future enhancement)

## Testing

Run manual tests using the comprehensive checklist:
```bash
# Review the testing guide
cat TESTING.md
```

**Test coverage includes**:
- 35+ test cases across 5 user stories
- Edge case validation
- Error handling verification
- Constitution compliance checks
- Cross-platform testing (Windows/macOS/Linux)

See `TESTING.md` for complete manual testing procedures.

## Constraints (Phase I)

**Explicitly Prohibited**:
- ❌ File system operations (no saving/loading)
- ❌ Database connections
- ❌ External dependencies (pip packages)
- ❌ Web frameworks or APIs
- ❌ Asynchronous/concurrent code
- ❌ AI features

**Technology Limits**:
- ✅ Python 3.13+ standard library only
- ✅ Cross-platform compatible (Windows/macOS/Linux)
- ✅ Single-user, single-session application

## Migration to Phase II

This codebase is designed for clean evolution:

| Phase I | Phase II (Future) |
|---------|------------------|
| `src/models.py` | → Add SQLAlchemy decorators |
| `src/store.py` | → Replace with repository pattern |
| `src/services.py` | → **Keep as-is** (zero changes!) |
| `src/cli.py` | → Replace with FastAPI routes |
| `main.py` | → Replace with uvicorn launcher |

**Validation**: Zero changes to `services.py` validates constitution principle V (Extensibility).

## Troubleshooting

### `python: command not found`
- Install Python 3.13+: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Try `python3` or `py` instead of `python`

### `uv: command not found`
- Install UV: [https://astral.sh/uv](https://astral.sh/uv)
- Or use standard `python -m venv` instead

### ModuleNotFoundError
- Ensure you're in the project root directory
- Activate virtual environment
- Verify `src/` directory exists with `__init__.py`

### Application won't start
1. Check Python version: `python --version` (must be 3.13+)
2. Verify project structure matches above
3. Try running from project root: `python main.py`

### Unicode encoding errors
- **Fixed in current version**: All Unicode symbols replaced with ASCII-safe alternatives
- Error messages now use `[OK]` and `[ERROR]` instead of checkmark/cross symbols
- No action needed for Windows users

## Documentation

- **Quick Setup**: See above or `specs/001-todo-console-app/quickstart.md`
- **Feature Spec**: `specs/001-todo-console-app/spec.md` (user stories, requirements)
- **Implementation Plan**: `specs/001-todo-console-app/plan.md` (architecture, decisions)
- **Task Breakdown**: `specs/001-todo-console-app/tasks.md` (development tasks)
- **Data Model**: `specs/001-todo-console-app/data-model.md` (entities, relationships)
- **API Contracts**: `specs/001-todo-console-app/contracts/services.md` (function signatures)
- **Manual Testing**: `TESTING.md` (comprehensive test checklist)

## Constitution

This project follows strict principles defined in `.specify/memory/constitution.md`:
1. **Simplicity Before Scalability** - Simple solutions first
2. **Clear Separation of Concerns** - Strict data/logic/UI layering
3. **Readability and Beginner-Friendly Code** - Educational code quality
4. **Deterministic Behavior** - No hidden state
5. **Extensibility for Future Phases** - Clean migration path to Phase II
6. **Input Validation and User-Friendly Errors** - Robust error handling

## License

[Specify license here]

## Contributing

[Specify contribution guidelines here]

## Support

For questions or issues:
1. Check `TESTING.md` for common scenarios
2. Review `specs/001-todo-console-app/quickstart.md`
3. Read `specs/001-todo-console-app/plan.md` for architecture details
4. Open a GitHub issue with:
   - Python version (`python --version`)
   - Operating system
   - Steps to reproduce
   - Error messages (full output)

---

**Phase I Complete** ✅

All 5 user stories implemented. Full CRUD functionality available.
Ready for manual testing and Phase II planning.
