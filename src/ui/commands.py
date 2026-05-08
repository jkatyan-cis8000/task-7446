"""
Command handlers for the habit tracker CLI.

This module provides individual command handlers that are dispatched from
the main CLI module. Each handler encapsulates the logic for a specific command,
including argument processing, service calls, and output formatting.
"""

import sys
from typing import Optional

import argparse

from src.runtime.app import HabitTrackerApp
from src.providers.date_utils import parse_date_string, today
from src.utils.formatters import format_table, format_streak_display, format_date


def cmd_add(app: HabitTrackerApp, args: argparse.Namespace) -> None:
    """
    Handle the 'add' command to create a new habit.

    Args:
        app: HabitTrackerApp instance
        args: Parsed command arguments containing name and description
    """
    try:
        habit_service = app.get_habit_service()
        habit = habit_service.add_habit(
            args.name, args.description if hasattr(args, 'description') else ""
        )
        print(f"✓ Habit '{habit.name}' created successfully (ID: {habit.habit_id})")
    except ValueError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(app: HabitTrackerApp, args: argparse.Namespace) -> None:
    """
    Handle the 'list' command to show all habits.

    Args:
        app: HabitTrackerApp instance
        args: Parsed command arguments (unused)
    """
    try:
        habit_service = app.get_habit_service()
        habits = habit_service.list_all_habits()

        if not habits:
            print("No habits found. Use 'add' to create one!")
            return

        # Prepare table data
        headers = ["ID", "Habit", "Description", "Created"]
        rows = [
            [
                str(h.habit_id),
                h.name,
                h.description[:30] + "..." if len(h.description) > 30 else h.description,
                format_date(h.created_date),
            ]
            for h in habits
        ]

        print(format_table(headers, rows))
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_log(app: HabitTrackerApp, args: argparse.Namespace) -> None:
    """
    Handle the 'log' command to record a habit completion.

    Args:
        app: HabitTrackerApp instance
        args: Parsed command arguments containing habit_id and optional date
    """
    try:
        logging_service = app.get_logging_service()

        # Parse habit_id
        try:
            habit_id = int(args.habit_id)
        except ValueError:
            print(f"✗ Error: Habit ID must be an integer", file=sys.stderr)
            sys.exit(1)

        # Parse date if provided, otherwise use today
        if hasattr(args, 'date') and args.date:
            try:
                completion_date = parse_date_string(args.date)
            except ValueError as e:
                print(f"✗ Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            completion_date = today()

        # Log the completion
        logging_service.log_date(habit_id, completion_date)
        print(
            f"✓ Logged completion for habit {habit_id} on "
            f"{format_date(completion_date)}"
        )
    except ValueError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_streaks(app: HabitTrackerApp, args: argparse.Namespace) -> None:
    """
    Handle the 'streaks' command to show weekly streak summaries.

    Args:
        app: HabitTrackerApp instance
        args: Parsed command arguments with optional habit_id
    """
    try:
        streak_service = app.get_streak_service()

        # If specific habit_id provided, show just that one
        if hasattr(args, 'habit_id') and args.habit_id:
            try:
                habit_id = int(args.habit_id)
                streak = streak_service.get_weekly_streak(habit_id)
                print(
                    format_streak_display(
                        streak.habit_id,
                        streak.days_completed,
                        streak.streak_status,
                    )
                )
            except ValueError as e:
                print(f"✗ Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Show all streaks in a table
            streaks = streak_service.get_all_weekly_streaks()

            if not streaks:
                print("No habits found to display streaks.")
                return

            headers = ["Habit ID", "Days Completed", "Status"]
            rows = [
                [s.habit_id, str(s.days_completed), s.streak_status]
                for s in streaks
            ]

            print(format_table(headers, rows))
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export(app: HabitTrackerApp, args: argparse.Namespace) -> None:
    """
    Handle the 'export' command to export habit data to CSV.

    Args:
        app: HabitTrackerApp instance
        args: Parsed command arguments with output_path and optional habit_ids
    """
    try:
        export_service = app.get_export_service()

        # Parse habit IDs if provided
        include_habits = None
        if hasattr(args, 'habit_ids') and args.habit_ids:
            try:
                include_habits = [int(hid) for hid in args.habit_ids]
            except ValueError:
                print(f"✗ Error: All habit IDs must be integers", file=sys.stderr)
                sys.exit(1)

        # Export to CSV
        export_service.export_to_csv(args.output_path, include_habits)
        print(f"✓ Data exported successfully to {args.output_path}")
    except ValueError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"✗ Error writing file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_help(app: HabitTrackerApp, args: argparse.Namespace) -> None:
    """
    Handle the 'help' command to show usage information.

    Args:
        app: HabitTrackerApp instance (unused)
        args: Parsed command arguments (unused)
    """
    help_text = """
Habit Tracker - Command Line Interface

Usage: python main.py <command> [arguments]

Commands:
  add <name> [description]
      Create a new habit
      Example: python main.py add "Morning Run" "30 minutes jogging"

  list
      Show all habits with IDs, names, descriptions, and creation dates

  log <habit_id> [date]
      Log a habit completion for today or a specific date
      Date format: YYYY-MM-DD
      Example: python main.py log 1 2024-05-08

  streaks [habit_id]
      Show weekly streak summaries for all habits or a specific habit

  export <output_path> [habit_ids...]
      Export habit data to CSV file
      Example: python main.py export habits.csv 1 2 3

  help
      Show this help message
    """
    print(help_text)
