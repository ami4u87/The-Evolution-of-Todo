"""
Entry point for the In-Memory Todo Console Application.

Run this file to start the todo application:
    python main.py
"""

from src.cli import run_cli


def main() -> None:
    """
    Entry point for the todo application.

    Launches the CLI interface.
    """
    run_cli()


if __name__ == "__main__":
    main()
