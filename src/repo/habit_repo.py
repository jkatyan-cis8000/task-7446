"""
Repository for Habit data access and CRUD operations.

This module provides the HabitRepository class that handles all database
operations related to habits, including creation, retrieval, update, and deletion.
"""

import sqlite3
from datetime import date
from typing import Optional, List

from src.types.models import Habit
from src.repo.database import HabitDB


class HabitRepository:
    """
    Data access layer for Habit operations.

    Provides CRUD operations for habits, translating database rows into
    Habit type objects and handling all SQL operations.
    """

    def __init__(self, db: HabitDB):
        """
        Initialize the HabitRepository with a database connection.

        Args:
            db: HabitDB instance for database access
        """
        self._db = db

    def create_habit(self, name: str, description: str) -> Habit:
        """
        Create a new habit in the database.

        Args:
            name: Unique name for the habit
            description: Description of the habit

        Returns:
            The created Habit object with assigned ID and created_date

        Raises:
            sqlite3.IntegrityError: If a habit with the same name already exists
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        created_date = date.today()

        cursor.execute(
            """
            INSERT INTO habits (name, description, created_date)
            VALUES (?, ?, ?)
        """,
            (name, description, created_date),
        )
        conn.commit()

        habit_id = cursor.lastrowid

        return Habit(
            name=name,
            description=description,
            habit_id=habit_id,
            created_date=created_date,
        )

    def get_habit(self, habit_id: int) -> Optional[Habit]:
        """
        Retrieve a habit by ID.

        Args:
            habit_id: The ID of the habit to retrieve

        Returns:
            The Habit object if found, None otherwise
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, description, created_date
            FROM habits
            WHERE id = ?
        """,
            (habit_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_habit(row)

    def list_habits(self) -> List[Habit]:
        """
        Retrieve all habits from the database.

        Returns:
            A list of all Habit objects, ordered by creation date
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, description, created_date
            FROM habits
            ORDER BY created_date
        """
        )

        rows = cursor.fetchall()

        return [self._row_to_habit(row) for row in rows]

    def update_habit(self, habit_id: int, name: str, description: str) -> None:
        """
        Update an existing habit.

        Args:
            habit_id: The ID of the habit to update
            name: New name for the habit
            description: New description for the habit

        Raises:
            sqlite3.IntegrityError: If the new name conflicts with another habit
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE habits
            SET name = ?, description = ?
            WHERE id = ?
        """,
            (name, description, habit_id),
        )

        conn.commit()

    def delete_habit(self, habit_id: int) -> None:
        """
        Delete a habit and all its associated completions.

        The foreign key constraint with ON DELETE CASCADE ensures that
        all completion records for this habit are also deleted.

        Args:
            habit_id: The ID of the habit to delete
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

        conn.commit()

    @staticmethod
    def _row_to_habit(row: sqlite3.Row) -> Habit:
        """
        Convert a database row to a Habit object.

        Args:
            row: A sqlite3.Row from a query result

        Returns:
            A Habit object
        """
        created_date = row["created_date"]
        # Convert string to date object if needed
        if isinstance(created_date, str):
            created_date = date.fromisoformat(created_date)

        return Habit(
            name=row["name"],
            description=row["description"],
            habit_id=row["id"],
            created_date=created_date,
        )
