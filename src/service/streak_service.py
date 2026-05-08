"""
Business logic for calculating habit streaks.

This service provides streak calculations based on completion history,
including weekly streak summaries for tracking habit progress.
"""

from datetime import date, timedelta
from typing import List

from src.types.models import Completion, Habit, WeeklyStreak
from src.repo.habit_repo import HabitRepository
from src.repo.completion_repo import CompletionRepository
from src.config.settings import DEFAULT_STREAK_THRESHOLD
from src.providers.date_utils import get_week_start, get_week_end, today


class StreakService:
    """
    Business logic service for calculating habit streaks.

    Provides methods for calculating weekly streaks and determining the
    current streak status based on completion history.
    """

    def __init__(
        self, habit_repo: HabitRepository, completion_repo: CompletionRepository
    ):
        """
        Initialize the StreakService with repositories.

        Args:
            habit_repo: HabitRepository for retrieving habits
            completion_repo: CompletionRepository for completion data
        """
        self._habit_repo = habit_repo
        self._completion_repo = completion_repo

    def get_weekly_streak(self, habit_id: int) -> WeeklyStreak:
        """
        Calculate the weekly streak for a habit.

        Returns the streak summary for the current week.

        Args:
            habit_id: The ID of the habit

        Returns:
            A WeeklyStreak object with the streak details

        Raises:
            ValueError: If the habit doesn't exist
        """
        # Validate habit exists
        habit = self._habit_repo.get_habit(habit_id)
        if habit is None:
            raise ValueError(f"Habit with ID {habit_id} not found")

        # Get current week boundaries
        current_date = today()
        week_start = get_week_start(current_date)
        week_end = get_week_end(current_date)

        # Get completions for this week
        completions = self._completion_repo.get_completions(
            habit_id, week_start, week_end
        )

        # Calculate days completed
        days_completed = self.calculate_streak(completions, week_start)

        # Determine streak status based on threshold
        status = "Active" if days_completed >= DEFAULT_STREAK_THRESHOLD else "Inactive"

        return WeeklyStreak(
            habit_id=str(habit_id),
            week_start_date=week_start,
            days_completed=days_completed,
            streak_status=status,
        )

    def get_all_weekly_streaks(self) -> List[WeeklyStreak]:
        """
        Get weekly streaks for all habits.

        Returns:
            A list of WeeklyStreak objects, one for each habit
        """
        habits = self._habit_repo.list_habits()
        streaks = []

        for habit in habits:
            try:
                streak = self.get_weekly_streak(habit.habit_id)
                streaks.append(streak)
            except ValueError:
                # Skip if habit lookup fails (shouldn't happen)
                pass

        return streaks

    @staticmethod
    def calculate_streak(completions: List[Completion], week_start: date) -> int:
        """
        Calculate the number of days completed in a week.

        Args:
            completions: List of Completion objects for the week
            week_start: The start date of the week

        Returns:
            The number of unique dates on which the habit was completed
        """
        # Get unique completion dates
        completion_dates = set(c.completion_date for c in completions)
        return len(completion_dates)
