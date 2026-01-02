# Tasks: In-Memory Todo Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/services.md

**Tests**: Manual testing only per constitution (no automated test framework in Phase I)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root
- Paths include exact module names from contracts/services.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per plan.md Phase 0

- [X] T001 Create src/ directory structure with __init__.py
- [X] T002 Initialize UV project with pyproject.toml (Python 3.13+, zero dependencies)
- [X] T003 [P] Create .python-version file (3.13)
- [X] T004 [P] Create .gitignore file (Python, venv, IDE patterns)
- [X] T005 [P] Create README.md with setup instructions skeleton

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data structures and storage layer that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 [P] Implement TodoItem dataclass in src/models.py with type hints and docstring
- [X] T007 Implement TodoStore class __init__ in src/store.py (initialize _todos list and _next_id counter)
- [X] T008 Implement TodoStore.add() method in src/store.py (auto-increment ID, set timestamp, default status="pending")
- [X] T009 Implement TodoStore.get_all() method in src/store.py (return all todos)
- [X] T010 Implement TodoStore.get_by_id() method in src/store.py (raise KeyError if not found)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and List Todos (Priority: P1) 🎯 MVP

**Goal**: Enable users to create new todos and view their todo list (minimum viable product)

**Independent Test**: Launch app, add 2-3 todos with different titles/descriptions, list them, verify unique IDs and "pending" status

### Implementation for User Story 1

- [X] T011 [P] [US1] Implement create_todo() service function in src/services.py (validate title non-empty, call store.add())
- [X] T012 [P] [US1] Implement list_todos() service function in src/services.py (delegate to store.get_all())
- [X] T013 [US1] Implement display_menu() function in src/cli.py (show numbered menu 1-6)
- [X] T014 [US1] Implement get_menu_choice() function in src/cli.py (prompt and validate numeric input)
- [X] T015 [US1] Implement handle_add_todo() function in src/cli.py (prompt for title/description, call create_todo service, display success/error)
- [X] T016 [US1] Implement handle_list_todos() function in src/cli.py (call list_todos service, format output with ID/title/status/created_at, handle empty list)
- [X] T017 [US1] Implement run_cli() main loop skeleton in src/cli.py (create TodoStore, display menu, route choice 1→add, 2→list, handle invalid choices)
- [X] T018 [US1] Create main.py entry point (import and call run_cli())

**Checkpoint**: At this point, users can create and list todos (MVP functional)

---

## Phase 4: User Story 5 - Exit Application Gracefully (Priority: P1) 🎯 MVP

**Goal**: Enable clean application exit with friendly message

**Independent Test**: Launch app, select Exit option, verify clean termination with goodbye message and no errors

### Implementation for User Story 5

- [X] T019 [US5] Add exit logic to run_cli() main loop in src/cli.py (menu choice 6, display goodbye message, break loop)
- [X] T020 [US5] Add Ctrl+C handler to run_cli() in src/cli.py (catch KeyboardInterrupt, display friendly exit message)

**Checkpoint**: MVP complete (Create/List + Exit working)

---

## Phase 5: User Story 2 - Mark Todos as Completed (Priority: P2)

**Goal**: Enable users to mark todos as completed and track progress

**Independent Test**: Create several todos (P1 functionality), mark specific ones completed by ID, verify status changes in list view

### Implementation for User Story 2

- [X] T021 [US2] Implement TodoStore.mark_completed() method in src/store.py (update status to "completed", raise KeyError if ID not found)
- [X] T022 [US2] Implement mark_as_completed() service function in src/services.py (delegate to store.mark_completed(), pass through KeyError)
- [X] T023 [US2] Implement handle_mark_completed() function in src/cli.py (prompt for ID, parse input, call mark_as_completed service, display success/error messages)
- [X] T024 [US2] Add menu choice 3 routing to run_cli() in src/cli.py (map to handle_mark_completed())

**Checkpoint**: Users can now create, list, and mark todos as completed

---

## Phase 6: User Story 3 - Delete Todos (Priority: P3)

**Goal**: Enable users to delete todos permanently

**Independent Test**: Create several todos, delete specific ones by ID, list remaining todos, verify deleted items no longer appear

### Implementation for User Story 3

- [X] T025 [US3] Implement TodoStore.delete() method in src/store.py (remove from _todos list, raise KeyError if ID not found)
- [X] T026 [US3] Implement delete_todo() service function in src/services.py (delegate to store.delete(), pass through KeyError)
- [X] T027 [US3] Implement handle_delete_todo() function in src/cli.py (prompt for ID, confirmation prompt y/n, call delete_todo service, display success/cancellation/error)
- [X] T028 [US3] Add menu choice 5 routing to run_cli() in src/cli.py (map to handle_delete_todo())

**Checkpoint**: Users can now create, list, complete, and delete todos

---

## Phase 7: User Story 4 - Update Todo Details (Priority: P4)

**Goal**: Enable users to update todo title and/or description

**Independent Test**: Create a todo, update its title and/or description, verify changes reflected in list view while ID and status unchanged

### Implementation for User Story 4

- [X] T029 [US4] Implement TodoStore.update() method in src/store.py (modify title/description if provided, raise KeyError if ID not found)
- [X] T030 [US4] Implement update_todo() service function in src/services.py (validate new_title if provided is non-empty, call store.update(), raise ValueError for empty title)
- [X] T031 [US4] Implement handle_update_todo() function in src/cli.py (prompt for ID, new title, new description, handle "press Enter to keep current", call update_todo service, display success/error)
- [X] T032 [US4] Add menu choice 4 routing to run_cli() in src/cli.py (map to handle_update_todo())

**Checkpoint**: All 5 user stories implemented - full CRUD functionality available

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, documentation, and testing artifacts

- [X] T033 [P] Complete README.md with full setup instructions, usage examples, and troubleshooting
- [X] T034 [P] Create TESTING.md manual test checklist mapping to all 5 user stories and edge cases
- [X] T035 Add input validation error handling for all CLI handlers in src/cli.py (catch ValueError for empty titles, KeyError for missing IDs, handle non-numeric input gracefully)
- [X] T036 Add docstrings to all functions in src/services.py (Args/Returns/Raises format per contracts/services.md)
- [X] T037 Add docstrings to all TodoStore methods in src/store.py
- [X] T038 Add docstrings to all CLI functions in src/cli.py
- [X] T039 Review code for constitution compliance: verify ZERO input()/print() in services.py, ZERO business logic in cli.py
- [X] T040 Run manual smoke test: full lifecycle (create → list → mark completed → update → delete → exit) works without errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1 - Create/List): Can start after Foundational - No dependencies on other stories
  - User Story 5 (P1 - Exit): Can start after User Story 1 - Needs run_cli() skeleton from US1
  - User Story 2 (P2 - Mark Completed): Can start after Foundational - Independent of US1/US5 but typically done after MVP
  - User Story 3 (P3 - Delete): Can start after Foundational - Independent of other stories
  - User Story 4 (P4 - Update): Can start after Foundational - Independent of other stories
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Create/List)**: No dependencies on other stories (depends only on Foundational phase)
- **User Story 5 (P1 - Exit)**: Depends on User Story 1 (needs run_cli() main loop skeleton)
- **User Story 2 (P2)**: Independent - can be built in parallel with US3/US4 after Foundational
- **User Story 3 (P3)**: Independent - can be built in parallel with US2/US4 after Foundational
- **User Story 4 (P4)**: Independent - can be built in parallel with US2/US3 after Foundational

### Within Each Phase

**Foundational Phase**:
- T006 (TodoItem dataclass) can be done in parallel with T007 (TodoStore __init__)
- T007-T010 (TodoStore methods) must be sequential (each method builds on __init__)

**User Story 1** (Create/List):
- T011 (create_todo service) and T012 (list_todos service) can be done in parallel
- T013 (display_menu) and T014 (get_menu_choice) can be done in parallel
- T015 (handle_add_todo) depends on T011 (create_todo service)
- T016 (handle_list_todos) depends on T012 (list_todos service)
- T017 (run_cli skeleton) depends on T013, T014
- T018 (main.py) depends on T017

**User Story 5** (Exit):
- T019 and T020 can be done in parallel (both modify run_cli())

**User Story 2** (Mark Completed):
- T021, T022, T023 must be sequential (store → service → CLI)
- T024 depends on T023

**User Story 3** (Delete):
- T025, T026, T027 must be sequential (store → service → CLI)
- T028 depends on T027

**User Story 4** (Update):
- T029, T030, T031 must be sequential (store → service → CLI)
- T032 depends on T031

**Polish Phase**:
- T033 (README) and T034 (TESTING.md) can be done in parallel
- T035-T039 can be done in parallel (different files)
- T040 (smoke test) must be last

### Parallel Opportunities

**Phase 2 (Foundational)**:
```bash
# Can run in parallel:
Task T006: [P] Implement TodoItem dataclass in src/models.py
Task T007: Implement TodoStore.__init__ in src/store.py
```

**Phase 3 (User Story 1)**:
```bash
# Can run in parallel:
Task T011: [P] [US1] Implement create_todo() service in src/services.py
Task T012: [P] [US1] Implement list_todos() service in src/services.py

# Can run in parallel:
Task T013: [US1] Implement display_menu() in src/cli.py
Task T014: [US1] Implement get_menu_choice() in src/cli.py
```

**Phase 8 (Polish)**:
```bash
# Can run in parallel:
Task T033: [P] Complete README.md
Task T034: [P] Create TESTING.md

# Can run in parallel:
Task T036: Add docstrings to src/services.py
Task T037: Add docstrings to src/store.py
Task T038: Add docstrings to src/cli.py
```

---

## Implementation Strategy

### MVP First (Phases 1-4 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T010) - **CRITICAL: blocks all user stories**
3. Complete Phase 3: User Story 1 - Create/List (T011-T018)
4. Complete Phase 4: User Story 5 - Exit (T019-T020)
5. **STOP and VALIDATE**: Test create, list, and exit functionality manually
6. Deploy/demo if ready (MVP complete!)

**MVP Scope**: Phases 1-4 = 20 tasks = ~200 LOC (models + store basics + services + CLI for add/list/exit)

### Incremental Delivery

1. **MVP** (Phases 1-4): Create/List + Exit → Test independently → Demo
2. **+Mark Completed** (Phase 5): Add P2 feature → Test independently → Demo
3. **+Delete** (Phase 6): Add P3 feature → Test independently → Demo
4. **+Update** (Phase 7): Add P4 feature → Test independently → Demo
5. **Polish** (Phase 8): Documentation, testing artifacts, final review

Each increment adds value without breaking previous features.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done, parallelize:**
   - Developer A: User Story 1 + 5 (MVP)
   - Developer B: User Story 2 (Mark Completed)
   - Developer C: User Story 3 (Delete)
   - Developer D: User Story 4 (Update)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label (e.g., [US1], [US2]) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing approach per constitution (no pytest/unittest in Phase I)
- Stop at any checkpoint to validate story independently
- All tasks reference exact file paths from contracts/services.md
- Constitution compliance verified in Phase 8 (T039)

---

## File Modification Summary

| File | Tasks | Purpose |
|------|-------|---------|
| `src/models.py` | T006 | TodoItem dataclass |
| `src/store.py` | T007-T010, T021, T025, T029 | TodoStore class with CRUD methods |
| `src/services.py` | T011-T012, T022, T026, T030, T036 | Business logic layer + validation |
| `src/cli.py` | T013-T017, T019-T020, T023-T024, T027-T028, T031-T032, T035, T038 | CLI handlers and main loop |
| `main.py` | T018 | Application entry point |
| `pyproject.toml` | T002 | UV project configuration |
| `.python-version` | T003 | Python version pinning |
| `.gitignore` | T004 | Git ignore rules |
| `README.md` | T005, T033 | Setup and usage instructions |
| `TESTING.md` | T034 | Manual test checklist |

**Total Tasks**: 40
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1 - Create/List): 8 tasks
- Phase 4 (US5 - Exit): 2 tasks
- Phase 5 (US2 - Mark Completed): 4 tasks
- Phase 6 (US3 - Delete): 4 tasks
- Phase 7 (US4 - Update): 4 tasks
- Phase 8 (Polish): 8 tasks

**Parallel Opportunities**: 11 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- ✅ US1: Add 2-3 todos, list them, verify IDs/status
- ✅ US5: Select exit, verify clean termination
- ✅ US2: Mark specific todos completed, verify status changes
- ✅ US3: Delete specific todos, verify removal
- ✅ US4: Update todo fields, verify changes reflected

**Suggested MVP Scope**: Phases 1-4 (20 tasks) delivers functional create/list/exit application
