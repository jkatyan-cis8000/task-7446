"""
Output formatting helpers for the habit tracker CLI.

This module provides pure formatting functions for displaying data to the user.
No domain logic or cross-layer imports. All functions are stateless utilities
for converting Python objects to human-readable strings.
"""

from datetime import date
from typing import List


def format_date(d: date) -> str:
    """
    Format a date object as an ISO 8601 string (YYYY-MM-DD).

    Args:
        d: A date object to format

    Returns:
        A string in YYYY-MM-DD format

    Raises:
        TypeError: If d is not a date object
    """
    if not isinstance(d, date):
        raise TypeError(f"Expected date object, got {type(d).__name__}")
    return d.strftime("%Y-%m-%d")


def parse_date_string(s: str) -> date:
    """
    Parse a date string in ISO 8601 format (YYYY-MM-DD).

    Args:
        s: A string in YYYY-MM-DD format

    Returns:
        A date object

    Raises:
        ValueError: If the string is not in valid YYYY-MM-DD format
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected string, got {type(s).__name__}")
    try:
        year, month, day = s.split("-")
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Invalid date format: {s!r}. Expected YYYY-MM-DD format."
        ) from e


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    Format a table with headers and rows as an ASCII table.

    Args:
        headers: List of column header strings
        rows: List of rows, where each row is a list of strings

    Returns:
        A formatted ASCII table as a string

    Raises:
        ValueError: If rows have inconsistent column counts
        TypeError: If headers or rows are not lists of strings
    """
    if not isinstance(headers, list):
        raise TypeError(f"headers must be a list, got {type(headers).__name__}")
    if not isinstance(rows, list):
        raise TypeError(f"rows must be a list, got {type(rows).__name__}")

    if not headers:
        raise ValueError("headers list cannot be empty")

    # Validate headers
    for h in headers:
        if not isinstance(h, str):
            raise TypeError(f"All headers must be strings, got {type(h).__name__}")

    # Validate rows and get column count
    if rows:
        col_count = len(headers)
        for row_idx, row in enumerate(rows):
            if not isinstance(row, list):
                raise TypeError(
                    f"Row {row_idx} is not a list, got {type(row).__name__}"
                )
            if len(row) != col_count:
                raise ValueError(
                    f"Row {row_idx} has {len(row)} columns, "
                    f"expected {col_count}"
                )
            for col_idx, cell in enumerate(row):
                if not isinstance(cell, str):
                    raise TypeError(
                        f"Row {row_idx}, column {col_idx} is not a string, "
                        f"got {type(cell).__name__}"
                    )

    # Calculate column widths
    col_widths = []
    for col_idx, header in enumerate(headers):
        max_width = len(header)
        for row in rows:
            max_width = max(max_width, len(row[col_idx]))
        col_widths.append(max_width)

    # Build the table
    lines = []

    # Header row
    header_cells = [
        h.ljust(col_widths[i]) for i, h in enumerate(headers)
    ]
    lines.append("  ".join(header_cells))

    # Separator line
    separator = "  ".join(
        "-" * width for width in col_widths
    )
    lines.append(separator)

    # Data rows
    for row in rows:
        row_cells = [
            cell.ljust(col_widths[i]) for i, cell in enumerate(row)
        ]
        lines.append("  ".join(row_cells))

    return "\n".join(lines)


def format_streak_display(
    habit_name: str, days_completed: int, status: str
) -> str:
    """
    Pretty print streak information for a single habit.

    Args:
        habit_name: Name of the habit
        days_completed: Number of days completed in the streak
        status: Status of the streak (e.g., "Active", "Inactive")

    Returns:
        A formatted string representation of the streak

    Raises:
        TypeError: If arguments are not of the expected types
        ValueError: If values are invalid
    """
    if not isinstance(habit_name, str) or not habit_name:
        raise TypeError("habit_name must be a non-empty string")
    if not isinstance(days_completed, int) or days_completed < 0:
        raise ValueError("days_completed must be a non-negative integer")
    if not isinstance(status, str) or not status:
        raise TypeError("status must be a non-empty string")

    # Format based on status
    status_symbol = "✓" if status.lower() == "active" else "○"

    return (
        f"{status_symbol} {habit_name}: {days_completed} "
        f"day{'s' if days_completed != 1 else ''} ({status})"
    )
