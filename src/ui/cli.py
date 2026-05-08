"""
Command-line interface for the habit tracker application.

This module provides the main CLI entry point with argument parsing and
command dispatch. Individual command handlers are in the commands module.
"""

import argparse
import sys
from typing import List, Optional

from src.runtime.app import HabitTrackerApp
from src.ui.commands import (
    cmd_add,
    cmd_list,
    cmd_log,
    cmd_streaks,
    cmd_export,
    cmd_help,
)


def main(argv: Optional[List[str]] = None) -> None:
    """
    Main CLI entry point with argument parsing and command dispatch.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])
    """
    if argv is None:
        argv = sys.argv[1:]

    # Create parser
    parser = argparse.ArgumentParser(
        prog="habit-tracker",
        description="A simple CLI habit tracker",
        add_help=False,  # We'll handle help manually
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new habit")
    add_parser.add_argument("name", help="Habit name")
    add_parser.add_argument(
        "description", nargs="?", default="", help="Habit description"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all habits")

    # Log command
    log_parser = subparsers.add_parser("log", help="Log a habit completion")
    log_parser.add_argument("habit_id", help="Habit ID to log")
    log_parser.add_argument(
        "date", nargs="?", help="Date in YYYY-MM-DD format (default: today)"
    )

    # Streaks command
    streaks_parser = subparsers.add_parser("streaks", help="Show weekly streaks")
    streaks_parser.add_argument(
        "habit_id", nargs="?", help="Optional: Show streak for specific habit"
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export data to CSV")
    export_parser.add_argument("output_path", help="Output CSV file path")
    export_parser.add_argument(
        "habit_ids", nargs="*", help="Optional: IDs of habits to export"
    )

    # Help command
    help_parser = subparsers.add_parser("help", help="Show help message")

    # Parse arguments
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("Use 'help' command for usage information", file=sys.stderr)
        sys.exit(1)

    # If no command provided, show help
    if not args.command:
        cmd_help(None, args)
        return

    # Initialize app
    app = HabitTrackerApp()
    try:
        app.initialize()

        # Dispatch to appropriate handler
        if args.command == "add":
            cmd_add(app, args)
        elif args.command == "list":
            cmd_list(app, args)
        elif args.command == "log":
            cmd_log(app, args)
        elif args.command == "streaks":
            cmd_streaks(app, args)
        elif args.command == "export":
            cmd_export(app, args)
        elif args.command == "help":
            cmd_help(app, args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
