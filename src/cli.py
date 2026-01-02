"""
Command-line interface for the todo application.

This module handles all user interaction (input/output) and delegates
business logic to the services layer. NO business logic in this module.
"""

from src.store import TodoStore
from src.services import (
    create_todo,
    list_todos,
    mark_as_completed,
    update_todo,
    delete_todo,
)


def display_menu() -> None:
    """
    Display the main menu options to the user.

    Output format:
        === Todo Application ===
        1. Add Todo
        2. List Todos
        3. Mark Todo as Completed
        4. Update Todo
        5. Delete Todo
        6. Exit
    """
    print("\n=== Todo Application ===")
    print("1. Add Todo")
    print("2. List Todos")
    print("3. Mark Todo as Completed")
    print("4. Update Todo")
    print("5. Delete Todo")
    print("6. Exit")
    print()


def get_menu_choice() -> int:
    """
    Prompt user for menu choice and return validated integer.

    Returns:
        int: User's menu choice (1-6)

    Notes:
        - Loops until valid integer is entered
        - Displays friendly error for non-numeric input
        - Does NOT validate range (handled by main loop)
    """
    while True:
        try:
            choice = int(input("Enter your choice (1-6): "))
            return choice
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number.")


def handle_add_todo(store: TodoStore) -> None:
    """
    Handle the "Add Todo" user interaction.

    Prompts:
        - "Enter todo title: "
        - "Enter description (optional, press Enter to skip): "

    Args:
        store: The TodoStore instance

    Side Effects:
        - Calls services.create_todo()
        - Prints success message with new todo ID
        - Prints error message if validation fails (empty title)
    """
    print("\n--- Add New Todo ---")
    title = input("Enter todo title: ")
    description = input("Enter description (optional, press Enter to skip): ")

    # Convert empty description to None
    if not description.strip():
        description = None

    try:
        todo = create_todo(store, title, description)
        print(f"[OK] Todo #{todo.id} created successfully!")
    except ValueError as e:
        print(f"[ERROR] {e}")


def handle_list_todos(store: TodoStore) -> None:
    """
    Handle the "List Todos" user interaction.

    Args:
        store: The TodoStore instance

    Side Effects:
        - Calls services.list_todos()
        - Prints formatted list of todos (or "No todos yet" if empty)

    Example Output:
        === Your Todos ===
        [1] Buy groceries (Pending)
            Created: 2026-01-02 10:30:15
            Description: Milk, eggs, bread

        [2] Read book (Completed)
            Created: 2026-01-02 11:45:22

        Or:
        No todos yet. Add your first task!
    """
    todos = list_todos(store)

    if not todos:
        print("\nNo todos yet. Add your first task!")
        return

    print("\n=== Your Todos ===")
    for todo in todos:
        status_display = "Completed" if todo.status == "completed" else "Pending"
        print(f"\n[{todo.id}] {todo.title} ({status_display})")
        print(f"    Created: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if todo.description:
            print(f"    Description: {todo.description}")


def handle_mark_completed(store: TodoStore) -> None:
    """
    Handle the "Mark Todo as Completed" user interaction.

    Prompts:
        - "Enter todo ID to mark as completed: "

    Args:
        store: The TodoStore instance

    Side Effects:
        - Calls services.mark_as_completed()
        - Prints success message
        - Prints error message if ID not found or invalid input
    """
    print("\n--- Mark Todo as Completed ---")
    try:
        todo_id = int(input("Enter todo ID to mark as completed: "))
        todo = mark_as_completed(store, todo_id)
        print(f"[OK] Todo #{todo.id} marked as completed!")
    except ValueError:
        print("[ERROR] Invalid ID. Please enter a number.")
    except KeyError as e:
        print(f"[ERROR] {e}")


def handle_update_todo(store: TodoStore) -> None:
    """
    Handle the "Update Todo" user interaction.

    Prompts:
        - "Enter todo ID to update: "
        - "Enter new title (or press Enter to keep current): "
        - "Enter new description (or press Enter to keep current): "

    Args:
        store: The TodoStore instance

    Side Effects:
        - Calls services.update_todo()
        - Prints success message
        - Prints error message if ID not found or validation fails
    """
    print("\n--- Update Todo ---")
    try:
        todo_id = int(input("Enter todo ID to update: "))

        # Get current todo to show existing values
        try:
            current_todo = store.get_by_id(todo_id)
            print(f"\nCurrent title: {current_todo.title}")
            print(
                f"Current description: {current_todo.description if current_todo.description else '(none)'}"
            )
        except KeyError as e:
            print(f"[ERROR] {e}")
            return

        new_title = input("\nEnter new title (or press Enter to keep current): ")
        new_description = input(
            "Enter new description (or press Enter to keep current): "
        )

        # Convert empty inputs to None (keep existing)
        if not new_title.strip():
            new_title = None
        if not new_description.strip():
            new_description = None

        todo = update_todo(store, todo_id, new_title, new_description)
        print(f"[OK] Todo #{todo.id} updated successfully!")
    except ValueError as e:
        if "Invalid literal" in str(e) or "invalid literal" in str(e):
            print("[ERROR] Invalid ID. Please enter a number.")
        else:
            print(f"[ERROR] {e}")
    except KeyError as e:
        print(f"[ERROR] {e}")


def handle_delete_todo(store: TodoStore) -> None:
    """
    Handle the "Delete Todo" user interaction.

    Prompts:
        - "Enter todo ID to delete: "
        - "Are you sure? This cannot be undone (y/n): "

    Args:
        store: The TodoStore instance

    Side Effects:
        - Calls services.delete_todo() if user confirms
        - Prints success message or cancellation message
        - Prints error message if ID not found or invalid input
    """
    print("\n--- Delete Todo ---")
    try:
        todo_id = int(input("Enter todo ID to delete: "))

        # Show todo details before confirming
        try:
            todo = store.get_by_id(todo_id)
            print(f"\nTodo to delete: [{todo.id}] {todo.title}")
        except KeyError as e:
            print(f"[ERROR] {e}")
            return

        confirmation = input("Are you sure? This cannot be undone (y/n): ").lower()

        if confirmation == "y" or confirmation == "yes":
            delete_todo(store, todo_id)
            print(f"[OK] Todo #{todo_id} deleted successfully!")
        else:
            print("Deletion cancelled.")
    except ValueError:
        print("[ERROR] Invalid ID. Please enter a number.")
    except KeyError as e:
        print(f"[ERROR] {e}")


def run_cli() -> None:
    """
    Main CLI loop for the todo application.

    Side Effects:
        - Creates TodoStore instance
        - Displays menu in loop
        - Routes user choices to appropriate handlers
        - Handles Ctrl+C gracefully (exit message)
        - Exits on choice 6 with goodbye message

    Example Output (on exit):
        Goodbye! Your todos were in-memory only (all data lost).

    Notes:
        - Infinite loop until user exits or Ctrl+C
        - Invalid menu choices display error and re-prompt
        - Catches and displays user-friendly messages for all exceptions
    """
    store = TodoStore()

    print("\n" + "=" * 50)
    print("Welcome to In-Memory Todo Console Application!")
    print("=" * 50)
    print("\nNote: All todos are stored in memory only.")
    print("Data will be lost when you exit the application.")

    try:
        while True:
            display_menu()
            choice = get_menu_choice()

            if choice == 1:
                handle_add_todo(store)
            elif choice == 2:
                handle_list_todos(store)
            elif choice == 3:
                handle_mark_completed(store)
            elif choice == 4:
                handle_update_todo(store)
            elif choice == 5:
                handle_delete_todo(store)
            elif choice == 6:
                print("\nGoodbye! Your todos were in-memory only (all data lost).")
                break
            else:
                print("[ERROR] Invalid choice. Please enter a number between 1 and 6.")

    except KeyboardInterrupt:
        print(
            "\n\nGoodbye! Your todos were in-memory only (all data lost)."
        )
