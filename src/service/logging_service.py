"""
Business logic for logging habit completions.

This service handles the creation and deletion of completion records,
delegating data access to the CompletionRepository and providing
business logic for completion management.
"""

from datetime import date

from src.types.models import Habit
from src.repo.habit_repo import HabitRepository
from src.repo.completion_repo import CompletionRepository
from src.providers.date_utils import today


class LoggingService:
    """
    Business logic service for logging habit completions.

    Provides operations for recording when habits are completed and undoing
    completions, with validation that habits exist before logging.
    """

    def __init__(
        self, habit_repo: HabitRepository, completion_repo: CompletionRepository
    ):
        """
        Initialize the LoggingService with repositories.

        Args:
            habit_repo: HabitRepository for habit validation
            completion_repo: CompletionRepository for completion data access
        """
        self._habit_repo = habit_repo
        self._completion_repo = completion_repo

    def log_today(self, habit_id: int) -> None:
        """
        Log a habit completion for today.

        Args:
            habit_id: The ID of the habit to log

        Raises:
            ValueError: If the habit doesn't exist
        """
        self.log_date(habit_id, today())

    def log_date(self, habit_id: int, completion_date: date) -> None:
        """
        Log a habit completion for a specific date.

        Args:
            habit_id: The ID of the habit to log
            completion_date: The date of the completion

        Raises:
            ValueError: If the habit doesn't exist
            TypeError: If completion_date is not a date object
        """
        # Validate habit exists
        habit = self._habit_repo.get_habit(habit_id)
        if habit is None:
            raise ValueError(f"Habit with ID {habit_id} not found")

        # Validate date is a date object
        if not isinstance(completion_date, date):
            raise TypeError("completion_date must be a date object")

        # Log the completion
        self._completion_repo.log_completion(habit_id, completion_date)

    def undo_completion(self, habit_id: int, completion_date: date) -> None:
        """
        Remove a completion record for a habit on a specific date.

        This deletes the completion record if it exists. If no completion
        exists for this date, this is a no-op (no error).

        Args:
            habit_id: The ID of the habit
            completion_date: The date of the completion to undo

        Raises:
            ValueError: If the habit doesn't exist
            TypeError: If completion_date is not a date object
        """
        # Validate habit exists
        habit = self._habit_repo.get_habit(habit_id)
        if habit is None:
            raise ValueError(f"Habit with ID {habit_id} not found")

        # Validate date is a date object
        if not isinstance(completion_date, date):
            raise TypeError("completion_date must be a date object")

        # Delete the completion record
        conn = self._completion_repo._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM completions
            WHERE habit_id = ? AND completion_date = ?
        """,
            (habit_id, completion_date),
        )

        conn.commit()
