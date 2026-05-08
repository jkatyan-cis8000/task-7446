"""Date and time utilities for the habit tracker application."""

from datetime import date, datetime, timedelta
from typing import List

from src.config.settings import WEEK_START_DAY


def today() -> date:
    """
    Get today's date.

    Returns:
        Current date
    """
    return datetime.now().date()


def get_week_start(d: date) -> date:
    """
    Get the start date of the week for a given date.

    Args:
        d: A date within the week

    Returns:
        The start date of the week (based on WEEK_START_DAY from config)
    """
    # Get the day of week (0=Monday, 6=Sunday)
    day_of_week = d.weekday()

    # Calculate days to subtract to get to week start
    days_to_subtract = (day_of_week - WEEK_START_DAY) % 7

    return d - timedelta(days=days_to_subtract)


def get_week_end(d: date) -> date:
    """
    Get the end date of the week for a given date.

    Args:
        d: A date within the week

    Returns:
        The end date of the week (6 days after week start)
    """
    week_start = get_week_start(d)
    return week_start + timedelta(days=6)


def date_range(start: date, end: date) -> List[date]:
    """
    Generate a list of dates from start to end (inclusive).

    Args:
        start: Start date (inclusive)
        end: End date (inclusive)

    Returns:
        List of dates from start to end
    """
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def parse_date_string(s: str) -> date:
    """
    Parse a date string in ISO format (YYYY-MM-DD).

    Args:
        s: Date string in ISO format

    Returns:
        Parsed date object

    Raises:
        ValueError: If the string is not in valid ISO format
    """
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format: {s}. Expected YYYY-MM-DD") from e


def format_date(d: date) -> str:
    """
    Format a date object as an ISO format string (YYYY-MM-DD).

    Args:
        d: Date to format

    Returns:
        Formatted date string
    """
    return d.strftime("%Y-%m-%d")
