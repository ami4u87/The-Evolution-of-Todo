# Manual Testing Checklist

This document provides a comprehensive manual testing checklist for the In-Memory Todo Console Application (Phase I).

## Test Environment Setup

1. Ensure Python 3.13+ is installed: `python --version`
2. Navigate to project root directory
3. Activate virtual environment (if created):
   - Windows: `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
4. Run application: `python main.py`

---

## User Story 1: Create and List Todos (P1 - MVP)

### Test 1.1: Create Todo with Title and Description
- [ ] Select option 1 (Add Todo)
- [ ] Enter title: "Buy groceries"
- [ ] Enter description: "Milk, eggs, bread"
- [ ] Verify success message displays with todo ID
- [ ] Expected: ✓ Todo #1 created successfully!

### Test 1.2: Create Todo with Title Only
- [ ] Select option 1 (Add Todo)
- [ ] Enter title: "Read book"
- [ ] Press Enter for description (leave empty)
- [ ] Verify success message displays with todo ID
- [ ] Expected: ✓ Todo #2 created successfully!

### Test 1.3: Create Todo with Empty Title (Validation)
- [ ] Select option 1 (Add Todo)
- [ ] Press Enter without entering title (leave empty)
- [ ] Enter any description
- [ ] Verify error message displays
- [ ] Expected: ✗ Error: Title cannot be empty

### Test 1.4: List All Todos
- [ ] Create 2-3 todos using Test 1.1 and 1.2
- [ ] Select option 2 (List Todos)
- [ ] Verify all todos display with:
  - Unique IDs (1, 2, 3...)
  - Titles
  - Status (Pending or Completed)
  - Created timestamps
  - Descriptions (if provided)

### Test 1.5: List Todos When Empty
- [ ] Start fresh application (no todos created)
- [ ] Select option 2 (List Todos)
- [ ] Verify friendly message displays
- [ ] Expected: "No todos yet. Add your first task!"

---

## User Story 5: Exit Application Gracefully (P1 - MVP)

### Test 5.1: Normal Exit
- [ ] Create a few todos
- [ ] Select option 6 (Exit)
- [ ] Verify goodbye message displays
- [ ] Expected: "Goodbye! Your todos were in-memory only (all data lost)."
- [ ] Verify application terminates cleanly (no errors)

### Test 5.2: Exit with Ctrl+C
- [ ] Create a few todos
- [ ] Press Ctrl+C at menu prompt
- [ ] Verify goodbye message displays
- [ ] Expected: "Goodbye! Your todos were in-memory only (all data lost)."
- [ ] Verify no stack trace or error messages

### Test 5.3: Data Loss on Exit (Expected Behavior)
- [ ] Create 3 todos
- [ ] Exit application (option 6)
- [ ] Restart application: `python main.py`
- [ ] Select option 2 (List Todos)
- [ ] Verify no todos exist (fresh start)
- [ ] Expected: "No todos yet. Add your first task!"

---

## User Story 2: Mark Todos as Completed (P2)

### Test 2.1: Mark Pending Todo as Completed
- [ ] Create 3 todos
- [ ] Select option 3 (Mark Todo as Completed)
- [ ] Enter ID: 2
- [ ] Verify success message
- [ ] Expected: ✓ Todo #2 marked as completed!
- [ ] List todos and verify todo #2 shows status "Completed"

### Test 2.2: Mark Non-Existent Todo (Error Handling)
- [ ] Create 2 todos
- [ ] Select option 3 (Mark Todo as Completed)
- [ ] Enter ID: 999
- [ ] Verify error message displays
- [ ] Expected: ✗ Error: Todo #999 not found

### Test 2.3: Mark Todo with Invalid ID Format
- [ ] Select option 3 (Mark Todo as Completed)
- [ ] Enter ID: "abc" (text instead of number)
- [ ] Verify error message displays
- [ ] Expected: ✗ Error: Invalid ID. Please enter a number.

### Test 2.4: Mark Already Completed Todo (Idempotent)
- [ ] Create a todo
- [ ] Mark it as completed
- [ ] Mark it as completed again (same ID)
- [ ] Verify it remains completed (no error)

---

## User Story 3: Delete Todos (P3)

### Test 3.1: Delete Todo with Confirmation
- [ ] Create 5 todos
- [ ] Select option 5 (Delete Todo)
- [ ] Enter ID: 3
- [ ] Verify todo details display for confirmation
- [ ] Enter confirmation: y
- [ ] Verify success message
- [ ] Expected: ✓ Todo #3 deleted successfully!
- [ ] List todos and verify todo #3 is gone

### Test 3.2: Cancel Delete Operation
- [ ] Create 3 todos
- [ ] Select option 5 (Delete Todo)
- [ ] Enter ID: 2
- [ ] Enter confirmation: n
- [ ] Verify cancellation message
- [ ] Expected: "Deletion cancelled."
- [ ] List todos and verify todo #2 still exists

### Test 3.3: Delete Last Remaining Todo
- [ ] Create 1 todo
- [ ] Delete it (with confirmation: y)
- [ ] List todos
- [ ] Verify empty list message displays
- [ ] Expected: "No todos yet. Add your first task!"

### Test 3.4: Delete Non-Existent Todo
- [ ] Select option 5 (Delete Todo)
- [ ] Enter ID: 999
- [ ] Verify error message before confirmation prompt
- [ ] Expected: ✗ Error: Todo #999 not found

---

## User Story 4: Update Todo Details (P4)

### Test 4.1: Update Title Only
- [ ] Create a todo with title "Buy grocerys" (typo)
- [ ] Select option 4 (Update Todo)
- [ ] Enter ID: 1
- [ ] Enter new title: "Buy groceries"
- [ ] Press Enter to keep description unchanged
- [ ] Verify success message
- [ ] List todos and verify title is corrected

### Test 4.2: Update Description Only
- [ ] Create a todo
- [ ] Select option 4 (Update Todo)
- [ ] Enter the todo ID
- [ ] Press Enter to keep title unchanged
- [ ] Enter new description: "Updated description"
- [ ] Verify success message
- [ ] List todos and verify description changed, title unchanged

### Test 4.3: Update Both Title and Description
- [ ] Create a todo
- [ ] Select option 4 (Update Todo)
- [ ] Enter the todo ID
- [ ] Enter new title: "New title"
- [ ] Enter new description: "New description"
- [ ] List todos and verify both fields updated

### Test 4.4: Update with Empty Title (Validation)
- [ ] Create a todo
- [ ] Select option 4 (Update Todo)
- [ ] Enter the todo ID
- [ ] Enter new title: (press Enter without typing)
- [ ] Enter description: "Some description"
- [ ] Verify original title is preserved (empty title rejected)

### Test 4.5: Update Non-Existent Todo
- [ ] Select option 4 (Update Todo)
- [ ] Enter ID: 999
- [ ] Verify error message displays
- [ ] Expected: ✗ Error: Todo #999 not found

---

## Edge Cases and Error Handling

### Test E1: Invalid Menu Choice
- [ ] At main menu, enter: 0
- [ ] Verify error message: ✗ Error: Invalid choice. Please enter a number between 1 and 6.
- [ ] At main menu, enter: 7
- [ ] Verify same error message

### Test E2: Non-Numeric Menu Input
- [ ] At main menu, enter: "abc"
- [ ] Verify error message: ✗ Error: Invalid input. Please enter a number.
- [ ] Verify menu re-displays

### Test E3: Special Characters in Title/Description
- [ ] Create todo with title: "Test café ☕"
- [ ] Create todo with description: "Line 1\nLine 2" (if terminal allows)
- [ ] List todos and verify special characters display correctly

### Test E4: Very Long Title/Description
- [ ] Create todo with 200+ character title
- [ ] Verify it accepts and displays the full title
- [ ] No hard limit expected (constitution: rely on terminal constraints)

### Test E5: ID Never Reused After Deletion
- [ ] Create todos with IDs 1, 2, 3
- [ ] Delete todo #2
- [ ] Create a new todo
- [ ] Verify new todo gets ID 4 (not reusing deleted ID 2)

---

## Full Lifecycle Test (Success Criteria SC-005)

Complete the full todo lifecycle in under 2 minutes:

1. [ ] Launch application: `python main.py`
2. [ ] Create a todo: "Task 1"
3. [ ] List todos (verify "Task 1" appears)
4. [ ] Mark todo as completed
5. [ ] List todos (verify status = "Completed")
6. [ ] Update todo title to "Task 1 Updated"
7. [ ] List todos (verify title changed)
8. [ ] Delete the todo
9. [ ] List todos (verify empty list)
10. [ ] Exit application

**Time requirement**: < 2 minutes
**Confusion level**: Zero (all commands clear)

---

## Cross-Platform Testing

### Windows
- [ ] Run `python main.py` on Windows 10/11
- [ ] Verify all features work
- [ ] Test Ctrl+C graceful exit

### macOS
- [ ] Run `python main.py` on macOS
- [ ] Verify all features work
- [ ] Test Ctrl+C graceful exit

### Linux
- [ ] Run `python main.py` on Linux
- [ ] Verify all features work
- [ ] Test Ctrl+C graceful exit

---

## Constitution Compliance Validation

### Test C1: Layer Separation (SC-006)
- [ ] Open `src/services.py`
- [ ] Verify ZERO occurrences of `input()` or `print()`
- [ ] Expected: All I/O must be in `src/cli.py` only

### Test C2: Docstring Coverage (SC-007)
- [ ] Open `src/models.py` - verify TodoItem has docstring
- [ ] Open `src/store.py` - verify all methods have docstrings
- [ ] Open `src/services.py` - verify all functions have docstrings
- [ ] Open `src/cli.py` - verify all functions have docstrings
- [ ] Expected: 100% docstring coverage

### Test C3: Type Hints
- [ ] Review all function signatures
- [ ] Verify all parameters have type hints
- [ ] Verify all return types annotated
- [ ] Expected: 100% type hint coverage

---

## Success Criteria Validation

- [ ] **SC-001**: Create 10 todos, list them, verify all 10 with unique IDs
- [ ] **SC-002**: Mark subset of todos as completed, verify status changes
- [ ] **SC-003**: Delete specific todos, verify they don't appear in list
- [ ] **SC-004**: Test all invalid inputs (verified in error handling tests above)
- [ ] **SC-005**: Complete full lifecycle in <2 minutes (see Full Lifecycle Test)
- [ ] **SC-006**: Verify layer separation (see Test C1)
- [ ] **SC-007**: Verify docstring coverage (see Test C2)
- [ ] **SC-008**: Application exits cleanly (see Test 5.1 and 5.2)

---

## Test Summary

**Total Test Cases**: 35+
**Phases Covered**: All 5 user stories + edge cases + constitution compliance

**Test Results** (fill in after testing):
- Tests Passed: ____/35
- Tests Failed: ____/35
- Issues Found: ____
- Critical Issues: ____

**Tester Name**: ________________
**Test Date**: ________________
**Platform Tested**: ________________
