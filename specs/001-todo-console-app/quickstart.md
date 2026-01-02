# Quickstart Guide: In-Memory Todo Console Application

**Feature**: 001-todo-console-app
**Created**: 2026-01-02
**Audience**: Developers setting up and running the application for the first time

## Prerequisites

Before you begin, ensure you have:

- **Python 3.13+** installed on your system
  - Check: `python --version` (should show 3.13.x or higher)
  - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)

- **UV package manager** installed
  - Check: `uv --version`
  - Install (Windows PowerShell): `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - Install (macOS/Linux): `curl -LsSf https://astral.sh/uv/install.sh | sh`

- **Git** (for cloning the repository)
  - Check: `git --version`

---

## Setup (First Time Only)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Hacathorn-II-phase-1-console-app
```

### Step 2: Create Virtual Environment

```bash
# Create a Python 3.13+ virtual environment using UV
uv venv --python 3.13

# Activate the virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.\.venv\Scripts\activate.bat

# macOS/Linux:
source .venv/bin/activate
```

**Verification**: Your terminal prompt should now show `(.venv)` prefix.

### Step 3: Verify No Dependencies

```bash
# Confirm no external packages are required
uv pip list
```

**Expected Output**: Only standard library packages (no external dependencies per constitution).

---

## Running the Application

### Launch the Todo App

```bash
# From the repository root (with virtual environment activated)
python main.py
```

### Expected Startup Screen

```
=== Todo Application ===
1. Add Todo
2. List Todos
3. Mark Todo as Completed
4. Update Todo
5. Delete Todo
6. Exit

Enter your choice (1-6):
```

---

## Usage Guide

### 1. Add a New Todo

```
Enter your choice (1-6): 1
Enter todo title: Buy groceries
Enter description (optional, press Enter to skip): Milk, eggs, bread

✓ Todo #1 created successfully!
```

### 2. List All Todos

```
Enter your choice (1-6): 2

=== Your Todos ===
[1] Buy groceries (Pending)
    Created: 2026-01-02 10:30:15
    Description: Milk, eggs, bread

[2] Read book (Pending)
    Created: 2026-01-02 11:45:22
```

**Empty List**:
```
Enter your choice (1-6): 2

No todos yet. Add your first task!
```

### 3. Mark Todo as Completed

```
Enter your choice (1-6): 3
Enter todo ID to mark as completed: 1

✓ Todo #1 marked as completed!
```

**Verification** (list again):
```
[1] Buy groceries (Completed)  ← Status changed
    Created: 2026-01-02 10:30:15
    Description: Milk, eggs, bread
```

### 4. Update a Todo

```
Enter your choice (1-6): 4
Enter todo ID to update: 1
Enter new title (or press Enter to keep current): Buy groceries and snacks
Enter new description (or press Enter to keep current):

✓ Todo #1 updated successfully!
```

**Keep Fields Unchanged**: Press Enter without typing to skip updating a field.

### 5. Delete a Todo

```
Enter your choice (1-6): 5
Enter todo ID to delete: 2
Are you sure? This cannot be undone (y/n): y

✓ Todo #2 deleted successfully!
```

**Cancel Deletion**: Enter `n` when prompted for confirmation.

### 6. Exit the Application

```
Enter your choice (1-6): 6

Goodbye! Your todos were in-memory only (all data lost).
```

**Important**: All todos are stored in memory only. When you exit, **all data is permanently lost** (by design for Phase I).

---

## Error Handling Examples

### Empty Title

```
Enter your choice (1-6): 1
Enter todo title:   (press Enter without typing)
Enter description (optional, press Enter to skip):

✗ Error: Title cannot be empty. Please try again.
```

### Non-Existent Todo ID

```
Enter your choice (1-6): 3
Enter todo ID to mark as completed: 999

✗ Error: Todo #999 not found.
```

### Invalid Input (Non-Numeric)

```
Enter your choice (1-6): abc

✗ Error: Invalid choice. Please enter a number between 1 and 6.
```

### Graceful Exit (Ctrl+C)

```
Enter your choice (1-6): ^C

Goodbye! Your todos were in-memory only (all data lost).
```

---

## Troubleshooting

### Problem: `python: command not found`

**Solution**:
- Ensure Python 3.13+ is installed: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- On Windows, try `python3` or `py` instead of `python`
- Restart terminal after installation

### Problem: `uv: command not found`

**Solution**:
- Install UV using the commands in Prerequisites section
- Restart terminal after installation
- On Windows, ensure `%USERPROFILE%\.cargo\bin` is in your PATH

### Problem: `ModuleNotFoundError: No module named 'src'`

**Solution**:
- Ensure you're running from the repository root directory
- Activate the virtual environment: `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (macOS/Linux)
- Verify project structure matches plan.md

### Problem: Application won't start

**Solution**:
1. Verify Python version: `python --version` (should be 3.13+)
2. Check virtual environment is activated (look for `(.venv)` in prompt)
3. Re-run setup steps from Step 1

---

## Development Workflow

### Making Changes

1. Activate virtual environment (if not already active)
2. Edit files in `src/` directory
3. Run application to test: `python main.py`
4. Repeat until feature works as expected

### Manual Testing

See `TESTING.md` for comprehensive manual test checklist covering:
- All user stories (P1-P4)
- Edge cases (empty lists, invalid IDs, special characters)
- Cross-platform validation (Windows, macOS, Linux)

### Code Style

Follow constitution guidelines:
- Descriptive variable names (`todo_id`, not `id`)
- Docstrings on all functions
- Type hints on all function signatures
- Comments explaining "why," not "what"

---

## Project Structure Reference

```
E:\Hacathorn-II-phase-1-console app\
├── src/
│   ├── __init__.py      # Package marker
│   ├── models.py        # TodoItem dataclass
│   ├── store.py         # TodoStore (in-memory storage)
│   ├── services.py      # Business logic (validation, CRUD)
│   └── cli.py           # CLI interface (user interaction)
├── main.py              # Application entry point
├── pyproject.toml       # UV configuration
├── .python-version      # Python version (3.13+)
├── README.md            # Project documentation
├── TESTING.md           # Manual test checklist
└── .gitignore           # Git ignore rules
```

---

## Frequently Asked Questions

### Q: Can I save my todos between sessions?

**A**: Not in Phase I. This version stores todos in memory only (all data lost on exit). Persistence will be added in Phase II with database integration.

### Q: Can I use Python 3.11 or 3.12 instead of 3.13?

**A**: The application requires Python 3.13+ per constitution and user requirements. Type hints use modern syntax (`str | None` instead of `Optional[str]`).

### Q: Are there any dependencies to install?

**A**: No. This application uses the Python standard library only (no `pip install` required). UV is used for environment management, not dependency installation.

### Q: Can I run this on macOS/Linux?

**A**: Yes! The application is cross-platform compatible. Follow the setup steps for macOS/Linux (mainly different virtual environment activation commands).

### Q: What happens if I create 1000+ todos?

**A**: The application can handle 1000+ todos (Python lists scale well), but the CLI output may become unwieldy. Future phases may add pagination.

### Q: Can I undo a delete operation?

**A**: No. Deletion is permanent in Phase I (no undo feature). The CLI prompts for confirmation (`y/n`) before deleting.

---

## Next Steps

- **Run Manual Tests**: See `TESTING.md` for full test checklist
- **Explore Code**: Read through `src/` modules to understand implementation
- **Report Issues**: Open GitHub issue for bugs or improvements
- **Plan Phase II**: Review migration path in `plan.md` for database integration

---

## Support

For questions or issues:
1. Check this quickstart guide
2. Review `TESTING.md` for common scenarios
3. Read `plan.md` for architecture details
4. Open a GitHub issue with:
   - Python version (`python --version`)
   - Operating system
   - Steps to reproduce issue
   - Error messages (full output)

---

**Enjoy building your todo list!** 🎯
