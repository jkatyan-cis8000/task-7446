"""
Business logic for habit management.

This service handles the creation, retrieval, update, and deletion of habits,
delegating all data access to the HabitRepository and providing a clean
interface for the UI layer.
"""

from src.types.models import Habit
from src.repo.habit_repo import HabitRepository


class HabitService:
    """
    Business logic service for habit operations.

    Provides high-level operations for managing habits, with error handling
    and validation at the business logic level.
    """

    def __init__(self, habit_repo: HabitRepository):
        """
        Initialize the HabitService with a repository.

        Args:
            habit_repo: HabitRepository instance for data access
        """
        self._habit_repo = habit_repo

    def add_habit(self, name: str, description: str) -> Habit:
        """
        Add a new habit to the tracker.

        Args:
            name: Unique name for the habit
            description: Description of the habit

        Returns:
            The created Habit object with assigned ID

        Raises:
            ValueError: If name or description are invalid
            sqlite3.IntegrityError: If a habit with this name already exists
        """
        # Validate inputs
        if not name or not isinstance(name, str):
            raise ValueError("Habit name must be a non-empty string")
        if not isinstance(description, str):
            raise ValueError("Habit description must be a string")

        name = name.strip()
        if not name:
            raise ValueError("Habit name cannot be empty or whitespace only")

        # Create the habit via repository
        habit = self._habit_repo.create_habit(name, description)
        return habit

    def list_all_habits(self) -> list[Habit]:
        """
        Get all habits in the tracker.

        Returns:
            A list of all Habit objects, ordered by creation date
        """
        return self._habit_repo.list_habits()

    def get_habit_details(self, habit_id: int) -> Habit:
        """
        Get details of a specific habit.

        Args:
            habit_id: The ID of the habit to retrieve

        Returns:
            The Habit object

        Raises:
            ValueError: If the habit is not found
        """
        habit = self._habit_repo.get_habit(habit_id)
        if habit is None:
            raise ValueError(f"Habit with ID {habit_id} not found")
        return habit

    def remove_habit(self, habit_id: int) -> None:
        """
        Delete a habit and all its completion records.

        Args:
            habit_id: The ID of the habit to delete

        Raises:
            ValueError: If the habit is not found
        """
        # Verify habit exists
        habit = self._habit_repo.get_habit(habit_id)
        if habit is None:
            raise ValueError(f"Habit with ID {habit_id} not found")

        # Delete the habit
        self._habit_repo.delete_habit(habit_id)
