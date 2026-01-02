# Implementation Plan: In-Memory Todo Console Application

**Branch**: `001-todo-console-app` | **Date**: 2026-01-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-todo-console-app/spec.md`

**Note**: This plan follows the Spec-Driven Development workflow and is designed for incremental, testable implementation.

## Summary

Build a command-line todo application in Python 3.13+ that stores tasks entirely in memory with full CRUD functionality. The application follows strict layered architecture (data/logic/UI) to ensure clean migration paths to future phases (FastAPI backend, database persistence, AI agents). Implementation uses UV for environment management, Python standard library only (no external dependencies), and delivers 5 user stories in priority order: P1 (Create/List + Exit MVP), P2 (Mark Completed), P3 (Delete), P4 (Update).

**Technical Approach**: Modular Python application with four core modules: `models.py` (Todo entity with type-safe data structures), `store.py` (in-memory storage with auto-incrementing IDs), `services.py` (business logic layer with validation and error handling), and `main.py` (CLI entry point with menu-driven interface). Each layer is strictly isolated per constitution principles to enable independent testing and future architectural evolution.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (`datetime`, `typing`, `dataclasses`)
**Storage**: In-memory only (Python lists/dicts), no persistence
**Testing**: Manual testing with documented test checklist (no pytest/unittest per constitution)
**Target Platform**: Cross-platform (Windows, macOS, Linux) console application
**Project Type**: Single project (simple structure with `src/` and manual tests)
**Performance Goals**: Sub-second response time for all operations (<100ms typical), handles 1000+ todos in memory comfortably
**Constraints**:
- No file system writes
- No database connections
- No external dependencies (pip packages prohibited)
- No async/threading
- Standard terminal I/O only (`input()`/`print()`)
- Session-scoped data lifetime (all data lost on exit)

**Scale/Scope**:
- Single-user, single-session application
- Designed for dozens of todos per session (up to 1000+ technically supported)
- 4 Python modules (~400-600 LOC total estimated)
- 5 user stories, 15 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ PASS: I. Simplicity Before Scalability
- **Rule**: Use simplest solution that fulfills requirements
- **Validation**: ✅ In-memory lists/dicts (simpler than database), standard library only (no external deps), function-based or lightweight classes (no complex patterns), menu-driven CLI (no command parser libraries)
- **Evidence**: No abstractions beyond basic class encapsulation, no ORM/repository patterns, no dependency injection frameworks

### ✅ PASS: II. Clear Separation of Concerns
- **Rule**: Strict boundaries between data/logic/UI layers
- **Validation**: ✅ Four-module architecture enforces separation:
  - `models.py`: Data structures only (TodoItem dataclass)
  - `store.py`: In-memory storage operations only (add, get, update, delete)
  - `services.py`: Business logic only (validation, error handling, state transitions)
  - `main.py`: CLI interaction only (input/output, menu display)
- **Gate**: Business logic (services) has ZERO `input()`/`print()` calls; UI layer has ZERO business logic
- **Evidence**: Clear module boundaries, function signatures enforce layer contracts

### ✅ PASS: III. Readability and Beginner-Friendly Code
- **Rule**: Readable by developers with basic Python knowledge
- **Validation**: ✅ Descriptive names (`create_todo`, `mark_as_completed`), docstrings on all functions, type hints on all signatures (Python 3.11+ syntax), inline comments for non-obvious logic
- **Gate**: 100% docstring coverage, no abbreviations except universally understood (id, UI, CLI)
- **Evidence**: Educational code quality; serves as learning resource

### ✅ PASS: IV. Deterministic Behavior (No Hidden State)
- **Rule**: Predictable behavior, explicit state changes
- **Validation**: ✅ Single global `TodoStore` instance (explicit), all state mutations through explicit methods (`add_todo`, `delete_todo`), no implicit ID reuse (monotonic counter), one-way status transitions (pending → completed)
- **Gate**: State changes only via documented function calls, no hidden mutations
- **Evidence**: TodoStore manages all state explicitly, IDs never reused

### ✅ PASS: V. Extensibility for Future Phases
- **Rule**: Code structure anticipates Phase II evolution
- **Validation**: ✅ Data model aligns with future DB schema (id, title, description, status, created_at), store operations map to future ORM/repository, validation logic reusable for API requests, business logic framework-agnostic
- **Gate**: Migration path documented: `models.py` → SQLAlchemy models, `store.py` → repository pattern, `services.py` → FastAPI route handlers
- **Evidence**: Clean abstractions enable swapping storage backend without touching business logic

### ✅ PASS: VI. Input Validation and User-Friendly Errors
- **Rule**: All inputs validated, graceful error handling
- **Validation**: ✅ Title validation (non-empty check), ID validation (existence check), type validation (int parsing with error handling), descriptive error messages (e.g., "Title cannot be empty", "Todo #X not found")
- **Gate**: 100% of invalid inputs handled without crashes (no unhandled exceptions)
- **Evidence**: Validation functions in services layer, try/except blocks in CLI layer

### Summary
**All 6 Constitution Gates: ✅ PASS**

No complexity violations detected. All design decisions follow simplest viable approach per constitution mandate. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-console-app/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (environment setup, best practices)
├── data-model.md        # Phase 1 output (TodoItem and TodoStore details)
├── quickstart.md        # Phase 1 output (setup and run instructions)
└── contracts/           # Phase 1 output (internal function signatures)
    └── services.md      # Service layer function contracts
```

### Source Code (repository root)

This is a **single project** structure (per constitution: simple console application).

```text
E:\Hacathorn-II-phase-1-console app\
├── src/
│   ├── __init__.py      # Package marker (can be empty)
│   ├── models.py        # TodoItem dataclass (data layer)
│   ├── store.py         # TodoStore class (storage layer)
│   ├── services.py      # Business logic functions (logic layer)
│   └── cli.py           # CLI interface functions (UI layer)
├── main.py              # Application entry point
├── pyproject.toml       # UV project configuration (Python 3.13+, no deps)
├── .python-version      # UV Python version pinning (3.13+)
├── README.md            # Setup and usage instructions
├── TESTING.md           # Manual test checklist (per constitution)
└── .gitignore           # Git ignore file (venv, __pycache__, etc.)
```

**Structure Decision**: Single project layout chosen because:
1. Simple console application (not web/mobile multi-tier)
2. Single entry point (`main.py`)
3. Four core modules fit cleanly in `src/` directory
4. No frontend/backend separation needed
5. Aligns with constitution principle: simplicity before scalability

**Testing Approach**: No `tests/` directory required per constitution (manual testing only). `TESTING.md` documents manual test scenarios mapped to user stories.

## Complexity Tracking

> **No violations detected**

All constitution checks passed. No complexity justifications required.

---

# Phase 0: Research & Environment Setup

*Prerequisites: Constitution Check passed (all gates ✅)*

## Objectives
1. Resolve any technical unknowns (NEEDS CLARIFICATION items)
2. Document UV environment setup best practices
3. Establish Python 3.13+ project conventions
4. Clarify dataclass vs. plain class approach for TodoItem

## Research Tasks

### R1: UV Environment Management
- **Question**: Best practices for initializing Python 3.13+ project with UV (no dependencies)
- **Decision**: Use `uv init` for project scaffolding, `uv venv --python 3.13` for environment creation
- **Rationale**: UV provides fast, reliable Python version management and virtual environment handling
- **Alternatives Considered**:
  - Manual venv creation: Less reliable, version conflicts
  - Poetry/pipenv: Overkill for zero-dependency project

### R2: Python Data Structures for TodoItem
- **Question**: Dataclass vs. plain class for TodoItem entity
- **Decision**: Use `@dataclass` from standard library (`dataclasses` module)
- **Rationale**:
  - Auto-generates `__init__`, `__repr__`, `__eq__` (less boilerplate)
  - Type hints built-in (constitution requirement)
  - Immutability option with `frozen=True` if needed
  - Standard library (no external dependency)
  - Readable by beginners (clear structure)
- **Alternatives Considered**:
  - Plain class: More boilerplate, manual `__init__` required
  - NamedTuple: Less flexible for optional fields (description)
  - Pydantic: External dependency (prohibited by constitution)

### R3: CLI Interface Style
- **Question**: Menu-driven (numbered options) vs. command-based interface
- **Decision**: **Menu-driven numbered interface** (1. Add Todo, 2. List Todos, etc.)
- **Rationale**:
  - Beginner-friendly (clear options presented each loop)
  - No command parsing logic needed (simpler)
  - Easier error handling (validate numeric input only)
  - Better discoverability (user sees all options)
- **Alternatives Considered**:
  - Command-based (`add`, `list`, `complete <id>`): Requires parsing, more complex error handling
  - Both approaches constitution-compliant; menu-driven is simpler

### R4: Timestamp Handling
- **Question**: UTC vs. local time for `created_at` timestamps
- **Decision**: **Local time** using `datetime.now()`
- **Rationale**:
  - Simpler implementation (no timezone library needed)
  - Single-user, single-session application (no timezone coordination)
  - Display matches user's system time (better UX)
  - Sufficient for Phase I (Phase II can add UTC if needed)
- **Alternatives Considered**:
  - UTC with `datetime.utcnow()`: Unnecessary complexity for console app

### R5: Error Handling Strategy
- **Question**: Exceptions vs. return codes for validation errors
- **Decision**: **Raise exceptions in services layer, catch and display in CLI layer**
- **Rationale**:
  - Pythonic approach (use exceptions for exceptional conditions)
  - Clean separation: services raise `ValueError`/`KeyError`, CLI catches and displays friendly messages
  - Easier to add error types later (extend exception hierarchy)
- **Alternatives Considered**:
  - Return tuples `(success: bool, error_msg: str)`: More boilerplate, less Pythonic

## Environment Setup Steps

### Step 1: Install UV (if not already installed)
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Initialize Project
```bash
cd "E:\Hacathorn-II-phase-1-console app"

# Initialize UV project (creates pyproject.toml)
uv init --name todo-console-app --no-readme

# Pin Python version to 3.13+
echo "3.13" > .python-version

# Create virtual environment
uv venv --python 3.13

# Activate environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
```

### Step 3: Create Project Structure
```bash
# Create source directory
mkdir src

# Create core module files
New-Item -ItemType File -Path src/__init__.py
New-Item -ItemType File -Path src/models.py
New-Item -ItemType File -Path src/store.py
New-Item -ItemType File -Path src/services.py
New-Item -ItemType File -Path src/cli.py

# Create main entry point
New-Item -ItemType File -Path main.py

# Create documentation files
New-Item -ItemType File -Path README.md
New-Item -ItemType File -Path TESTING.md
```

### Step 4: Configure pyproject.toml
```toml
[project]
name = "todo-console-app"
version = "1.0.0"
description = "In-Memory Python Console-Based Todo Application (Phase I)"
requires-python = ">=3.13"
dependencies = []  # No external dependencies

[project.scripts]
todo = "main:main"  # Entry point for running the app
```

### Step 5: Create .gitignore
```text
# Python
__pycache__/
*.py[cod]
*$py.class
.Python

# Virtual environments
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## Validation Checklist

Before proceeding to Phase 1:
- [ ] UV installed and accessible (`uv --version` succeeds)
- [ ] Python 3.13+ available (`python --version` shows 3.13.x)
- [ ] Virtual environment created and activated
- [ ] Project structure matches plan
- [ ] `pyproject.toml` configured with Python 3.13+ requirement
- [ ] No external dependencies listed
- [ ] `.gitignore` prevents committing venv and cache files

---

**Output**: `research.md` created with decisions documented (see above integrated directly into plan for Phase I).

---

# Phase 1: Design & Contracts

*Prerequisites: Phase 0 complete (environment setup validated)*

## Data Model Design

See `data-model.md` for complete entity definitions, field types, and validation rules.

**Summary**:
- **TodoItem**: Dataclass with `id`, `title`, `description`, `status`, `created_at`
- **TodoStore**: Class managing in-memory list of TodoItem objects with auto-incrementing ID counter

## API Contracts (Internal Function Signatures)

See `contracts/services.md` for complete service layer function signatures, parameter types, return types, and exceptions raised.

**Summary**: 15 functions across 4 modules
- **models.py**: TodoItem dataclass (1 class)
- **store.py**: 7 storage operations (add, get_all, get_by_id, update, delete, etc.)
- **services.py**: 5 business logic functions (create_todo, list_todos, mark_completed, update_todo, delete_todo)
- **cli.py**: Main menu loop and command handlers

## Quickstart Guide

See `quickstart.md` for complete setup and usage instructions.

**Summary**:
1. Clone repository
2. Install UV
3. Create virtual environment: `uv venv --python 3.13`
4. Activate environment
5. Run application: `python main.py`
6. Follow menu prompts (1-6 for operations, 7 to exit)

## Implementation Sequence (from user input)

### Step 1: UV Environment Setup ✅
*Completed in Phase 0*

### Step 2: Project Structure ✅
*Completed in Phase 0*

### Step 3: Todo Domain Model
**File**: `src/models.py`

Implement `TodoItem` dataclass with:
- `id: int` - Unique identifier
- `title: str` - Required task description
- `description: str | None` - Optional details
- `status: str` - "pending" or "completed" (literal type)
- `created_at: datetime` - Timestamp

**Constitution Compliance**:
- ✅ No I/O logic (data structure only)
- ✅ Type hints on all fields
- ✅ Docstring explaining purpose

### Step 4: In-Memory Store
**File**: `src/store.py`

Implement `TodoStore` class with:
- `_todos: list[TodoItem]` - Private in-memory storage
- `_next_id: int` - Auto-incrementing ID counter
- Methods: `add()`, `get_all()`, `get_by_id()`, `update()`, `delete()`, `mark_completed()`

**Constitution Compliance**:
- ✅ Explicit state management (no hidden mutations)
- ✅ ID generation deterministic (monotonic counter)
- ✅ Methods raise exceptions for invalid operations (e.g., KeyError for non-existent ID)

### Step 5: Business Logic Layer
**File**: `src/services.py`

Implement service functions:
- `create_todo(store, title, description)` - Validates title, calls store.add()
- `list_todos(store)` - Returns all todos (delegates to store.get_all())
- `update_todo(store, todo_id, new_title, new_description)` - Validates and updates
- `mark_as_completed(store, todo_id)` - Changes status to "completed"
- `delete_todo(store, todo_id)` - Removes todo from store

**Constitution Compliance**:
- ✅ ZERO `input()` or `print()` calls (pure business logic)
- ✅ Validation logic reusable for future API endpoints
- ✅ Clear error messages via exceptions

### Step 6: CLI Interface
**File**: `src/cli.py` and `main.py`

Implement menu-driven interface:
- Display numbered menu (1-7: Add, List, Update, Mark Complete, Delete, Exit)
- Collect user input
- Map choices to service functions
- Display success/error messages
- Handle Ctrl+C gracefully (exit message)

**Constitution Compliance**:
- ✅ All I/O contained in CLI layer
- ✅ ZERO business logic in UI code (delegates to services)
- ✅ Friendly error messages for invalid inputs

### Step 7: Manual Testing & Cleanup
**File**: `TESTING.md`

Create manual test checklist covering:
- All 5 user stories (P1-P4)
- Each acceptance scenario
- Edge cases (empty list, invalid IDs, special characters, etc.)
- Cross-platform validation (Windows, macOS, Linux)

**Constitution Compliance**:
- ✅ Manual testing approach (no automated framework per constitution)
- ✅ Test scenarios map to success criteria

## Agent Context Update

After completing Phase 1 design artifacts, run:

```powershell
# Windows
.specify\scripts\powershell\update-agent-context.ps1 -AgentType claude

# This updates CLAUDE.md with:
# - Python 3.13+ technology context
# - UV environment management notes
# - Standard library only constraint
# - Module structure (models, store, services, cli)
```

---

# Phase 2: Re-evaluation

*Prerequisites: Phase 1 complete (data-model.md, contracts/, quickstart.md created)*

## Constitution Check Re-evaluation

### ✅ PASS: All Gates Still Met

Post-design validation confirms:
1. **Simplicity**: No new complexity introduced; dataclass and simple classes only
2. **Separation of Concerns**: Four-module architecture enforced in contracts
3. **Readability**: All function signatures documented with type hints and docstrings
4. **Deterministic Behavior**: Explicit state management in TodoStore design
5. **Extensibility**: Data model aligns with future DB schema (Phase II ready)
6. **Input Validation**: Validation layer documented in services contracts

**No regressions detected**. Proceed to `/sp.tasks` for task generation.

---

# Implementation Workflow Summary

## Pre-Implementation Checklist

Before running `/sp.tasks`:
- [x] Constitution Check passed (all 6 gates ✅)
- [x] Phase 0 research complete (environment setup documented)
- [x] Phase 1 design complete (data-model.md, contracts/, quickstart.md created)
- [x] Technical Context fully specified (no NEEDS CLARIFICATION remaining)
- [x] Project structure defined (single project, 4 modules)
- [x] Agent context updated (CLAUDE.md refreshed with Python 3.13+ context)

## Next Command

```bash
/sp.tasks
```

This will generate `tasks.md` with:
- Dependency-ordered tasks organized by user story (P1 MVP first)
- Exact file paths for each task
- Parallel execution opportunities marked `[P]`
- Test tasks if required (manual testing per constitution)
- Implementation phases aligned with 7-step plan above

## Expected Artifacts

After `/sp.tasks` and `/sp.implement`:
- `src/models.py` - TodoItem dataclass (~40 LOC)
- `src/store.py` - TodoStore class (~120 LOC)
- `src/services.py` - Business logic functions (~150 LOC)
- `src/cli.py` - CLI interface (~100 LOC)
- `main.py` - Entry point (~20 LOC)
- `README.md` - Setup instructions (~50 lines)
- `TESTING.md` - Manual test checklist (~80 lines)
- `pyproject.toml` - UV configuration (~15 lines)

**Total Estimated LOC**: ~430 lines of Python code + ~145 lines of documentation

## Migration Path to Phase II

When transitioning to Phase II (FastAPI + Database):
1. **models.py** → Add SQLAlchemy decorators to TodoItem (`@mapped_column`, etc.)
2. **store.py** → Replace with repository pattern using SQLAlchemy session
3. **services.py** → Keep as-is (business logic unchanged)
4. **cli.py** → Replace with FastAPI route handlers (`@app.post("/todos")`, etc.)
5. **main.py** → Replace with `uvicorn.run(app)` or FastAPI CLI

**Validation**: Zero changes to services.py validates constitution principle V (Extensibility).

---

## Architectural Decision Record (ADR) Opportunities

The following design decisions may warrant ADR documentation (suggest after `/sp.tasks`):

1. **ADR-001: Dataclass for TodoItem Entity**
   - Decision: Use `@dataclass` instead of plain class or NamedTuple
   - Context: Need type-safe, readable data structure with minimal boilerplate
   - Tradeoffs: Dataclass vs. plain class vs. NamedTuple vs. Pydantic

2. **ADR-002: Menu-Driven CLI Interface**
   - Decision: Numbered menu (1-7) vs. command-based interface (`add`, `list`, etc.)
   - Context: Balance simplicity, discoverability, and error handling
   - Tradeoffs: Menu vs. commands vs. hybrid approach

3. **ADR-003: Exception-Based Error Handling**
   - Decision: Raise exceptions in services, catch in CLI
   - Context: Clean separation between layers, Pythonic error handling
   - Tradeoffs: Exceptions vs. return tuples vs. result objects

**Suggestion**: Run `/sp.adr` after implementation to document these decisions for future reference and team learning.

---

## Notes

- This plan integrates the user-provided 7-step outline with constitution requirements
- All decisions prioritize simplicity (constitution principle I)
- Layer boundaries are strictly enforced (constitution principle II)
- Data model is extensible to Phase II (constitution principle V)
- No external dependencies (constitution technology standards)
- Manual testing approach aligns with constitution (no automated framework in Phase I)

**Status**: Ready for `/sp.tasks` command to generate actionable task list.
