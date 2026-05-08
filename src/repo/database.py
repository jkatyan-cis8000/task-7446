"""
SQLite database management for the habit tracker application.

This module handles database connection management, schema initialization,
and provides the core database interface for all repository classes.
"""

import sqlite3
from pathlib import Path
from typing import Optional

from src.config.settings import DB_PATH, create_db_directory


class HabitDB:
    """
    Manages SQLite database connections and schema for the habit tracker.

    This class is responsible for:
    - Creating and managing database connections
    - Initializing the database schema on first use
    - Providing a single point of database access for repositories
    - Clean shutdown of database connections
    """

    def __init__(self):
        """Initialize the HabitDB instance."""
        self._connection: Optional[sqlite3.Connection] = None
        self._db_path = DB_PATH

    def get_connection(self) -> sqlite3.Connection:
        """
        Get or create the database connection.

        Creates a new connection if one doesn't exist, using row factory
        for convenient row access.

        Returns:
            An active sqlite3 Connection object
        """
        if self._connection is None:
            # Ensure database directory exists
            create_db_directory()

            # Create connection
            self._connection = sqlite3.connect(self._db_path)
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Use Row factory for convenient access
            self._connection.row_factory = sqlite3.Row

        return self._connection

    def init_db(self) -> None:
        """
        Initialize the database schema.

        Creates the habits and completions tables if they don't exist.
        Idempotent - safe to call multiple times.

        Tables created:
        - habits: Stores habit definitions with unique names
        - completions: Stores completion logs with foreign key to habits
        - Indexes on completions for efficient querying
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create habits table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_date DATE NOT NULL
            )
        """
        )

        # Create completions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY,
                habit_id INTEGER NOT NULL,
                completion_date DATE NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                UNIQUE(habit_id, completion_date)
            )
        """
        )

        # Create index for efficient querying by habit_id and date
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_completions_habit_date
            ON completions(habit_id, completion_date)
        """
        )

        conn.commit()

    def close(self) -> None:
        """
        Close the database connection.

        Safe to call even if no connection is open.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
