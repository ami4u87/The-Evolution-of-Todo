# Feature Specification: In-Memory Todo Console Application

**Feature Branch**: `001-todo-console-app`
**Created**: 2026-01-02
**Status**: Draft
**Input**: User description: "Build a command-line todo application that stores tasks entirely in memory with all basic CRUD-style functionality"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and List Todos (Priority: P1) 🎯 MVP

As a user, I want to create new todo items and view my todo list so that I can track tasks I need to complete.

**Why this priority**: This is the absolute minimum viable product. Without the ability to create and view todos, the application has no value. This story delivers immediate utility and can be independently demonstrated.

**Independent Test**: Can be fully tested by launching the app, adding 2-3 todos with different titles and descriptions, listing them, and verifying they appear correctly with unique IDs and "pending" status.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I select "Add Todo" and enter title "Buy groceries" with description "Milk, eggs, bread", **Then** a new todo is created with a unique ID, status "pending", and a timestamp
2. **Given** I have added 3 todos, **When** I select "List Todos", **Then** all 3 todos are displayed with their ID, title, status, and creation time in a readable format
3. **Given** the application is running with no todos, **When** I select "List Todos", **Then** I see a friendly message like "No todos yet. Add your first task!"
4. **Given** I try to add a todo, **When** I leave the title empty, **Then** I receive an error message "Title cannot be empty" and am prompted to try again
5. **Given** I add a todo with only a title (no description), **When** I list todos, **Then** the todo appears with its title and no description field shown

---

### User Story 2 - Mark Todos as Completed (Priority: P2)

As a user, I want to mark todo items as completed so that I can track my progress and distinguish finished tasks from pending ones.

**Why this priority**: Completion tracking is the second most critical feature for a todo app. It builds on P1 (create/list) to provide the core workflow: add task → complete task. This delivers the primary value proposition of task management.

**Independent Test**: Can be tested independently by creating several todos (using P1 functionality), marking specific ones as completed by ID, and verifying the status changes from "pending" to "completed" in the list view.

**Acceptance Scenarios**:

1. **Given** I have 3 pending todos (IDs 1, 2, 3), **When** I select "Mark Completed" and enter ID 2, **Then** todo #2's status changes to "completed" and the list shows this change
2. **Given** I try to mark a todo as completed, **When** I enter a non-existent ID like 999, **Then** I receive an error message "Todo #999 not found" and can try again
3. **Given** I have a todo that is already marked as completed, **When** I try to mark it completed again, **Then** I receive a friendly message "Todo #X is already completed"
4. **Given** I try to mark a todo as completed, **When** I enter invalid input like "abc", **Then** I receive an error message "Invalid ID. Please enter a number" and can try again

---

### User Story 3 - Delete Todos (Priority: P3)

As a user, I want to delete todo items so that I can remove tasks that are no longer relevant or were created by mistake.

**Why this priority**: Deletion is important for cleanup but not essential for the basic workflow. Users can work effectively without deletion (just ignore unwanted items), making this lower priority than create/list/complete.

**Independent Test**: Can be tested independently by creating several todos, deleting specific ones by ID, listing remaining todos, and verifying the deleted items no longer appear.

**Acceptance Scenarios**:

1. **Given** I have 5 todos (IDs 1-5), **When** I select "Delete Todo" and enter ID 3, **Then** todo #3 is permanently removed and the list shows only 4 todos
2. **Given** I try to delete a todo, **When** I enter a non-existent ID, **Then** I receive an error message "Todo #X not found. Cannot delete." and can try again
3. **Given** I have one todo remaining, **When** I delete it, **Then** the list becomes empty and shows "No todos yet" message
4. **Given** I try to delete a todo, **When** I enter invalid input like empty string or text, **Then** I receive an error message "Invalid ID. Please enter a number"

---

### User Story 4 - Update Todo Details (Priority: P4)

As a user, I want to update the title or description of existing todos so that I can correct mistakes or refine task details without deleting and recreating items.

**Why this priority**: Update functionality is convenient but not essential for basic task management. Users can work around missing updates by deleting and recreating todos. This is a quality-of-life feature that enhances usability but doesn't unlock new workflows.

**Independent Test**: Can be tested independently by creating a todo, updating its title and/or description, and verifying the changes are reflected in the list view while ID and status remain unchanged.

**Acceptance Scenarios**:

1. **Given** I have a todo with title "Buy grocerys" (typo), **When** I select "Update Todo", enter the ID, and change title to "Buy groceries", **Then** the title is corrected and description remains unchanged
2. **Given** I have a todo, **When** I update only its description, **Then** the description changes and title remains unchanged
3. **Given** I try to update a todo, **When** I enter a non-existent ID, **Then** I receive an error message "Todo #X not found. Cannot update."
4. **Given** I try to update a todo's title, **When** I provide an empty title, **Then** I receive an error message "Title cannot be empty" and the original title is preserved
5. **Given** I update a todo, **When** I choose to keep the existing title/description unchanged, **Then** those fields remain as they were

---

### User Story 5 - Exit Application Gracefully (Priority: P1) 🎯 MVP

As a user, I want to exit the application cleanly so that I can end my session without errors or confusion.

**Why this priority**: Graceful exit is part of the MVP core experience. An application that can't be exited properly feels broken and creates user frustration. This is a basic usability requirement.

**Independent Test**: Can be tested by launching the app, performing any operation (or none), selecting "Exit" or "Quit", and verifying the application terminates cleanly with a friendly goodbye message and no errors.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I select "Exit" or "Quit", **Then** the application terminates cleanly with a message like "Goodbye! Your session has ended."
2. **Given** I have unsaved todos (in-memory), **When** I exit, **Then** I am reminded "Your todos will be lost (in-memory only)" and the app exits cleanly
3. **Given** the application is at the main menu, **When** I use Ctrl+C or similar interrupt signal, **Then** the application catches it gracefully and exits with a friendly message (no stack trace)

---

### Edge Cases

- **Empty List Operations**: What happens when trying to mark completed, delete, or update when no todos exist? → Show friendly message "No todos available. Add a todo first."
- **ID Boundaries**: What happens with ID overflow (e.g., after creating 1000+ todos in a session)? → IDs increment indefinitely using Python's unbounded integers; no practical limit in Phase I.
- **Special Characters**: How does the system handle titles/descriptions with newlines, tabs, or special Unicode? → Accept all valid UTF-8 input; display as-is (no sanitization needed for console output).
- **Concurrent ID Gaps**: After deleting todos, are IDs reused? → No. IDs are auto-incremented and never reused within a session (simple counter pattern).
- **Maximum Input Length**: Is there a limit on title/description length? → No hard limit in Phase I; rely on terminal input constraints. Constitution principle: keep simple.
- **Status Transitions**: Can a completed todo be marked as pending again? → Not in Phase I. Status flow is one-way: pending → completed. (Future enhancement opportunity.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create a new todo item with a required title and optional description
- **FR-002**: System MUST auto-generate a unique integer ID for each todo item starting from 1 and incrementing sequentially
- **FR-003**: System MUST assign a "pending" status to newly created todos by default
- **FR-004**: System MUST capture a creation timestamp for each todo using the current system time
- **FR-005**: System MUST display all todo items in a readable list format showing ID, title, status, and creation time
- **FR-006**: System MUST provide a "Mark Completed" operation that changes a todo's status from "pending" to "completed"
- **FR-007**: System MUST provide a "Delete Todo" operation that permanently removes a todo from the in-memory store
- **FR-008**: System MUST provide an "Update Todo" operation that allows modifying the title and/or description of an existing todo
- **FR-009**: System MUST validate that todo titles are non-empty strings before creation or update
- **FR-010**: System MUST validate that todo IDs provided by users exist in the current in-memory store before operations
- **FR-011**: System MUST provide clear error messages for invalid inputs (empty titles, non-existent IDs, invalid ID formats)
- **FR-012**: System MUST handle invalid user input without crashing (e.g., text where number expected, empty input)
- **FR-013**: System MUST provide a "Quit" or "Exit" command that terminates the application cleanly
- **FR-014**: System MUST display a main menu or command prompt showing available operations to the user
- **FR-015**: System MUST maintain all todo data in memory only (no file system writes, no database connections)

### Key Entities *(include if feature involves data)*

- **TodoItem**: Represents a single task in the todo list
  - `id` (int): Unique identifier, auto-incremented starting from 1
  - `title` (str): Required, non-empty description of the task
  - `description` (str | None): Optional additional details about the task
  - `status` (str): One of "pending" or "completed" (enumerated values)
  - `created_at` (datetime): Timestamp when the todo was created (UTC or local time)

- **TodoStore**: In-memory container for all todo items
  - Manages the collection of TodoItem objects
  - Provides ID generation (simple counter)
  - Enforces uniqueness of IDs within the runtime session
  - Implements core operations: add, get_all, get_by_id, update, delete, mark_completed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can successfully create 10 todos, list them, and see all 10 with unique IDs and correct data (100% accuracy)
- **SC-002**: User can mark any subset of todos as completed and verify status changes immediately in the list view (100% success rate)
- **SC-003**: User can delete specific todos by ID and verify they no longer appear in the list (100% accuracy, no phantom todos)
- **SC-004**: Application handles 100% of invalid inputs gracefully (empty titles, bad IDs, wrong data types) without crashes or stack traces
- **SC-005**: User completes the full lifecycle (create → list → mark completed → update → delete → exit) in under 2 minutes with zero confusion about available commands
- **SC-006**: Codebase maintains strict separation: 0 `input()` or `print()` calls in business logic layer, 0 business logic in UI layer (validated by code review)
- **SC-007**: 100% of functions include docstrings with type hints (validated by manual inspection or static analysis)
- **SC-008**: Application exits cleanly with no error messages or stack traces when user selects "Quit" (100% success rate)

## Out of Scope *(explicitly excluded)*

The following are **NOT** part of this Phase I specification:

- **Persistence**: No file system storage, no database integration, no saving/loading todos between sessions
- **Web Interface**: No REST API, no web UI, no HTTP endpoints
- **Authentication**: No user accounts, no login, no multi-user support
- **Advanced Queries**: No search functionality, no filtering by status/date, no sorting options
- **Undo/Redo**: No command history, no undo operations
- **Bulk Operations**: No "delete all completed", no "mark all as completed", no multi-select
- **Categories/Tags**: No labels, no categories, no hierarchical organization
- **Due Dates**: No deadlines, no reminders, no date-based features
- **Priority Levels**: No high/medium/low priority, no urgency indicators
- **AI Features**: No natural language processing, no smart suggestions, no AI assistants
- **Export/Import**: No JSON export, no CSV import, no data migration tools
- **Testing Framework**: No pytest, no unittest integration (manual testing only per constitution)
- **Configuration**: No settings files, no user preferences, no customization options
- **Logging**: No file-based logs, no log levels (simple print statements for errors acceptable)

## Technical Guidance *(informative, not prescriptive)*

The implementation plan (`plan.md`) will detail the technical approach, but this specification suggests:

**Architecture Layers** (per constitution):
- **Data Layer**: `TodoStore` class managing in-memory list of `TodoItem` objects
- **Logic Layer**: Service functions for CRUD operations (create_todo, list_todos, mark_completed, etc.)
- **UI Layer**: CLI interface handling menu display, input collection, output formatting

**Technology Constraints**:
- Python 3.13+ (as specified by user)
- UV for environment management (per user requirements)
- Standard library only (datetime, typing, dataclasses or simple classes)
- No external packages (no rich, no click, no pydantic)

**User Interface Style** (implementation choice):
- Option A: Numbered menu (1. Add Todo, 2. List Todos, etc.)
- Option B: Command-based (`add`, `list`, `complete <id>`, etc.)
- Either approach is acceptable; prioritize clarity and simplicity

**Data Validation Patterns**:
- Title validation: `if not title.strip(): raise ValueError("Title cannot be empty")`
- ID validation: Check existence in store before operations
- Type validation: Handle ValueError/TypeError for numeric inputs

## Assumptions & Clarifications

- **Single User**: One person uses the application in one terminal session (no concurrency concerns)
- **English Language**: All prompts and error messages in English (no i18n requirements)
- **Terminal Compatibility**: Assumes standard terminal capabilities (no color support required, plain text output)
- **Time Zone**: Timestamps use system local time (no UTC conversion needed for Phase I)
- **Data Lifetime**: All todos exist only during the application runtime; exiting loses all data (by design)
- **ID Assignment**: IDs start at 1 and increment; deleted IDs are not reused (simplest approach)

## Dependencies & Prerequisites

- Python 3.13+ installed on user's system
- UV package manager installed and configured
- Standard library modules: `datetime`, `typing`, `dataclasses` (or manual class definitions)
- Terminal/console access (command line environment)

## Next Steps

After specification approval:

1. **Run `/sp.plan`** to create the implementation plan with:
   - Technical architecture details (project structure, module organization)
   - Constitution compliance checks
   - Data model documentation
   - API contracts (internal function signatures)
   - Quickstart guide for running the application

2. **Run `/sp.tasks`** to generate actionable, dependency-ordered tasks based on the user stories and plan

3. **Run `/sp.implement`** to execute the task-driven implementation workflow

## Notes

- This specification follows the constitution principle of "Simplicity Before Scalability"—every requirement is the minimum needed for Phase I
- User stories are prioritized to enable incremental delivery: P1 stories (Create/List + Exit) form the MVP
- Each user story is independently testable per constitution requirements
- The specification intentionally avoids implementation details (those belong in `plan.md`)
- Edge cases are documented but handled with simple, graceful error messages (no complex state machines)
