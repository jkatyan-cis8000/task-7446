"""Output formatting utilities for the habit tracker CLI."""

from datetime import date
from typing import List


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    Format data as a nicely aligned ASCII table.

    Args:
        headers: List of column headers
        rows: List of rows, where each row is a list of strings

    Returns:
        Formatted table as a string

    Raises:
        ValueError: If headers are empty or rows have inconsistent column counts
    """
    if not headers:
        raise ValueError("Headers list cannot be empty")

    if not rows:
        # Return header-only table
        return _format_table_rows(headers, [])

    # Validate row lengths
    for row in rows:
        if len(row) != len(headers):
            raise ValueError(
                f"Row length {len(row)} does not match headers length {len(headers)}"
            )

    return _format_table_rows(headers, rows)


def _format_table_rows(headers: List[str], rows: List[List[str]]) -> str:
    """
    Internal function to format table with proper alignment.

    Args:
        headers: List of column headers
        rows: List of rows

    Returns:
        Formatted table string
    """
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Build the table
    lines = []

    # Header separator
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    lines.append(separator)

    # Header row
    header_row = "|"
    for i, h in enumerate(headers):
        header_row += f" {h.ljust(col_widths[i])} |"
    lines.append(header_row)

    # Header separator
    lines.append(separator)

    # Data rows
    for row in rows:
        data_row = "|"
        for i, cell in enumerate(row):
            data_row += f" {cell.ljust(col_widths[i])} |"
        lines.append(data_row)

    # Bottom separator
    lines.append(separator)

    return "\n".join(lines)


def format_date(d: date) -> str:
    """
    Format a date object as an ISO format string (YYYY-MM-DD).

    Args:
        d: Date to format

    Returns:
        Formatted date string

    Raises:
        TypeError: If input is not a date object
    """
    if not isinstance(d, date):
        raise TypeError(f"Expected date object, got {type(d).__name__}")
    return d.strftime("%Y-%m-%d")


def parse_date_string(s: str) -> date:
    """
    Parse a date string in ISO format (YYYY-MM-DD).

    Args:
        s: Date string in ISO format

    Returns:
        Parsed date object

    Raises:
        ValueError: If the string is not in valid ISO format
        TypeError: If input is not a string
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected string, got {type(s).__name__}")

    try:
        parts = s.split("-")
        if len(parts) != 3:
            raise ValueError("Date string must contain exactly 3 parts (YYYY-MM-DD)")

        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])

        return date(year, month, day)
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid date format: {s}. Expected YYYY-MM-DD") from e


def format_streak_display(
    habit_name: str, days_completed: int, status: str
) -> str:
    """
    Format a streak summary for display.

    Args:
        habit_name: Name of the habit
        days_completed: Number of days completed in the week
        status: Current status of the streak (e.g., "Active", "Inactive")

    Returns:
        Formatted streak display string

    Raises:
        TypeError: If arguments are not the correct type
        ValueError: If values are invalid
    """
    if not isinstance(habit_name, str) or not habit_name:
        raise ValueError("Habit name must be a non-empty string")

    if not isinstance(days_completed, int) or days_completed < 0:
        raise ValueError("Days completed must be a non-negative integer")

    if not isinstance(status, str) or not status:
        raise ValueError("Status must be a non-empty string")

    progress_bar = _build_progress_bar(days_completed)

    return (
        f"{habit_name}: {days_completed}/7 days\n"
        f"  {progress_bar}\n"
        f"  Status: {status}"
    )


def _build_progress_bar(days_completed: int, width: int = 7) -> str:
    """
    Build a simple progress bar visualization.

    Args:
        days_completed: Number of days completed
        width: Width of the progress bar (default 7 for week days)

    Returns:
        Progress bar string
    """
    filled = min(days_completed, width)
    empty = width - filled
    return "[" + "█" * filled + "░" * empty + "]"
