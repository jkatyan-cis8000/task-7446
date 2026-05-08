"""
Core data types for the habit tracker application.

This module defines the fundamental data structures used throughout the system:
- Habit: Represents a single habit that a user wants to track
- Completion: Represents a single day on which a habit was completed
- WeeklyStreak: Represents a weekly summary of habit completions
- HabitExport: Represents habit data formatted for CSV export

Pure type definitions with no business logic or cross-layer imports.
"""

from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class Habit:
    """
    Represents a habit to be tracked.

    Attributes:
        name: Unique identifier for the habit (e.g., "Reading")
        description: Optional description of the habit
        habit_id: Unique integer ID assigned by the database
        created_date: Date when the habit was created
    """

    name: str
    description: str
    habit_id: int
    created_date: date

    def __post_init__(self):
        """Validate habit attributes after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Habit name must be a non-empty string")
        if not isinstance(self.description, str):
            raise ValueError("Habit description must be a string")
        if not isinstance(self.habit_id, int) or self.habit_id <= 0:
            raise ValueError("Habit ID must be a positive integer")
        if not isinstance(self.created_date, date):
            raise ValueError("Created date must be a date object")

    def __repr__(self):
        """Return a readable representation of the Habit."""
        return (
            f"Habit(name={self.name!r}, description={self.description!r}, "
            f"habit_id={self.habit_id}, created_date={self.created_date})"
        )


@dataclass
class Completion:
    """
    Represents a single completion of a habit on a specific date.

    Attributes:
        habit_id: The ID of the habit that was completed
        completion_date: The date on which the habit was completed
    """

    habit_id: int
    completion_date: date

    def __post_init__(self):
        """Validate completion attributes after initialization."""
        if not isinstance(self.habit_id, int) or self.habit_id <= 0:
            raise ValueError("Habit ID must be a positive integer")
        if not isinstance(self.completion_date, date):
            raise ValueError("Completion date must be a date object")

    def __repr__(self):
        """Return a readable representation of the Completion."""
        return (
            f"Completion(habit_id={self.habit_id}, "
            f"completion_date={self.completion_date})"
        )


@dataclass
class WeeklyStreak:
    """
    Represents a weekly streak summary for a habit.

    Attributes:
        habit_id: The ID of the habit (stored as string for compatibility)
        week_start_date: The start date of the week
        days_completed: Number of days the habit was completed during the week
        streak_status: Current status of the streak (e.g., "Active", "Inactive")
    """

    habit_id: str
    week_start_date: date
    days_completed: int
    streak_status: str

    def __post_init__(self):
        """Validate weekly streak attributes after initialization."""
        if not self.habit_id or not isinstance(self.habit_id, str):
            raise ValueError("Habit ID must be a non-empty string")
        if not isinstance(self.week_start_date, date):
            raise ValueError("Week start date must be a date object")
        if not isinstance(self.days_completed, int) or self.days_completed < 0:
            raise ValueError("Days completed must be a non-negative integer")
        if not self.streak_status or not isinstance(self.streak_status, str):
            raise ValueError("Streak status must be a non-empty string")

    def __repr__(self):
        """Return a readable representation of the WeeklyStreak."""
        return (
            f"WeeklyStreak(habit_id={self.habit_id!r}, "
            f"week_start_date={self.week_start_date}, "
            f"days_completed={self.days_completed}, "
            f"streak_status={self.streak_status!r})"
        )


@dataclass
class HabitExport:
    """
    Represents habit data formatted for export (e.g., to CSV).

    Attributes:
        habit_name: The name of the habit
        completed_dates: List of dates (as strings) when the habit was completed
        current_streak: The current streak count for the habit
    """

    habit_name: str
    completed_dates: List[str]
    current_streak: int

    def __post_init__(self):
        """Validate habit export attributes after initialization."""
        if not self.habit_name or not isinstance(self.habit_name, str):
            raise ValueError("Habit name must be a non-empty string")
        if not isinstance(self.completed_dates, list):
            raise ValueError("Completed dates must be a list")
        for date_str in self.completed_dates:
            if not isinstance(date_str, str):
                raise ValueError("All completed dates must be strings")
        if not isinstance(self.current_streak, int) or self.current_streak < 0:
            raise ValueError("Current streak must be a non-negative integer")

    def __repr__(self):
        """Return a readable representation of the HabitExport."""
        return (
            f"HabitExport(habit_name={self.habit_name!r}, "
            f"completed_dates={self.completed_dates!r}, "
            f"current_streak={self.current_streak})"
        )
