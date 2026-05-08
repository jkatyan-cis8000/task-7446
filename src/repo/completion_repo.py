"""
Repository for Completion data access and querying.

This module provides the CompletionRepository class that handles all database
operations related to habit completions, including logging completions and
querying completion history.
"""

import sqlite3
from datetime import date
from typing import List

from src.types.models import Completion
from src.repo.database import HabitDB


class CompletionRepository:
    """
    Data access layer for Completion operations.

    Provides methods for logging habit completions and querying completion
    history, translating database rows into Completion type objects.
    """

    def __init__(self, db: HabitDB):
        """
        Initialize the CompletionRepository with a database connection.

        Args:
            db: HabitDB instance for database access
        """
        self._db = db

    def log_completion(self, habit_id: int, completion_date: date) -> None:
        """
        Log a habit completion for a specific date.

        If a completion already exists for this habit and date, this is a no-op
        (enforced by the UNIQUE constraint).

        Args:
            habit_id: The ID of the habit being completed
            completion_date: The date on which the habit was completed

        Raises:
            sqlite3.IntegrityError: If the habit_id doesn't exist or if
                                    a completion already exists for this date
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO completions (habit_id, completion_date)
            VALUES (?, ?)
        """,
            (habit_id, completion_date),
        )

        conn.commit()

    def get_completions(
        self, habit_id: int, start_date: date, end_date: date
    ) -> List[Completion]:
        """
        Retrieve all completions for a habit within a date range.

        Args:
            habit_id: The ID of the habit
            start_date: The start date of the range (inclusive)
            end_date: The end date of the range (inclusive)

        Returns:
            A list of Completion objects for dates when the habit was completed,
            ordered by date
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT habit_id, completion_date
            FROM completions
            WHERE habit_id = ? AND completion_date >= ? AND completion_date <= ?
            ORDER BY completion_date
        """,
            (habit_id, start_date, end_date),
        )

        rows = cursor.fetchall()

        return [self._row_to_completion(row) for row in rows]

    def has_completion(self, habit_id: int, completion_date: date) -> bool:
        """
        Check if a habit has a completion logged for a specific date.

        Args:
            habit_id: The ID of the habit
            completion_date: The date to check

        Returns:
            True if the habit was completed on the given date, False otherwise
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1 FROM completions
            WHERE habit_id = ? AND completion_date = ?
            LIMIT 1
        """,
            (habit_id, completion_date),
         )

        return cursor.fetchone() is not None

    @staticmethod
    def _row_to_completion(row: sqlite3.Row) -> Completion:
        """
        Convert a database row to a Completion object.

        Args:
            row: A sqlite3.Row from a query result

        Returns:
            A Completion object
        """
        completion_date = row["completion_date"]
        # Convert string to date object if needed
        if isinstance(completion_date, str):
            completion_date = date.fromisoformat(completion_date)

        return Completion(
            habit_id=row["habit_id"],
            completion_date=completion_date,
        )
