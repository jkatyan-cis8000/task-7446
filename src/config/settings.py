"""Configuration constants for habit tracker application."""

import os
from pathlib import Path


# Database configuration
DB_DIR = Path.home() / ".habit_tracker"
DB_PATH = os.getenv("HABIT_TRACKER_DB", str(DB_DIR / "habits.db"))

# Streak configuration
DEFAULT_STREAK_THRESHOLD = int(os.getenv("HABIT_TRACKER_STREAK_THRESHOLD", "1"))

# Week configuration (0 = Monday, 6 = Sunday)
WEEK_START_DAY = int(os.getenv("HABIT_TRACKER_WEEK_START_DAY", "0"))


def create_db_directory() -> None:
    """Ensure database directory exists."""
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
