"""
Business logic for CSV export functionality.

This module provides the ExportService class which handles exporting habit data
to CSV format with completion history and streak information.
"""

from datetime import date
from typing import Optional, List

from src.types.models import HabitExport
from src.repo.habit_repo import HabitRepository
from src.repo.completion_repo import CompletionRepository
from src.providers.csv_writer import write_csv
from src.providers.date_utils import format_date, today


class ExportService:
    """
    Business logic service for exporting habit data.

    Handles exporting habit completion data to CSV format with summary
    information. Supports exporting all habits or a filtered subset.
    """

    def __init__(
        self,
        habit_repo: HabitRepository,
        completion_repo: CompletionRepository,
    ):
        """
        Initialize the ExportService with repositories.

        Args:
            habit_repo: HabitRepository for accessing habits
            completion_repo: CompletionRepository for accessing completions
        """
        self._habit_repo = habit_repo
        self._completion_repo = completion_repo

    def export_to_csv(
        self, filepath: str, include_habits: Optional[List[int]] = None
    ) -> None:
        """
        Export habit data to a CSV file.

        Exports habit names, completion dates, and current streak information.
        If include_habits is None, exports all habits.

        Args:
            filepath: Path where the CSV file should be written
            include_habits: List of habit IDs to export (None = all habits)

        Raises:
            ValueError: If filepath is invalid
            IOError: If the file cannot be written
        """
        if not filepath or not isinstance(filepath, str):
            raise ValueError("filepath must be a non-empty string")

        # Get habits to export
        all_habits = self._habit_repo.list_habits()

        if include_habits is not None:
            if not isinstance(include_habits, list):
                raise ValueError("include_habits must be a list or None")
            # Filter habits by ID
            habit_map = {h.habit_id: h for h in all_habits}
            habits_to_export = [
                habit_map[hid] for hid in include_habits if hid in habit_map
            ]
        else:
            habits_to_export = all_habits

        # Prepare data for export
        headers = ["Habit", "Week Starting", "Days Completed", "Status"]
        rows = []

        for habit in habits_to_export:
            export_data = self.prepare_export_data(habit.habit_id)

            # Create row for current week
            row = [
                export_data.habit_name,
                self._get_current_week_start(),
                str(len(export_data.completed_dates)),
                self._get_status(export_data.current_streak),
            ]
            rows.append(row)

        # Write CSV file
        write_csv(filepath, headers, rows)

    def prepare_export_data(self, habit_id: int) -> HabitExport:
        """
        Prepare habit data for export.

        Gathers completion history and current streak information for a habit.

        Args:
            habit_id: The ID of the habit to export

        Returns:
            A HabitExport object with completion data

        Raises:
            ValueError: If habit_id is invalid
            LookupError: If habit not found
        """
        if not isinstance(habit_id, int) or habit_id <= 0:
            raise ValueError("Habit ID must be a positive integer")

        # Get habit info
        habit = self._habit_repo.get_habit(habit_id)
        if habit is None:
            raise LookupError(f"Habit with ID {habit_id} not found")

        # Get all completions (no date limit)
        conn = self._completion_repo._db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT completion_date FROM completions
            WHERE habit_id = ?
            ORDER BY completion_date
        """,
            (habit_id,),
        )

        rows = cursor.fetchall()
        completed_dates = [
            format_date(
                row["completion_date"]
                if isinstance(row["completion_date"], date)
                else date.fromisoformat(row["completion_date"])
            )
            for row in rows
        ]

        # Get current streak (days in current week)
        current_streak = self._get_current_week_completion_count(habit_id)

        return HabitExport(
            habit_name=habit.name,
            completed_dates=completed_dates,
            current_streak=current_streak,
        )

    @staticmethod
    def _get_current_week_start() -> str:
        """
        Get the current week start date as a formatted string.

        Returns:
            Current week start date in YYYY-MM-DD format
        """
        from src.providers.date_utils import get_week_start

        return format_date(get_week_start(today()))

    def _get_current_week_completion_count(self, habit_id: int) -> int:
        """
        Count completions for a habit in the current week.

        Args:
            habit_id: The ID of the habit

        Returns:
            Number of days completed this week
        """
        from src.providers.date_utils import get_week_start, get_week_end

        week_start = get_week_start(today())
        week_end = get_week_end(today())

        completions = self._completion_repo.get_completions(
            habit_id, week_start, week_end
        )

        return len(completions)

    @staticmethod
    def _get_status(current_streak: int) -> str:
        """
        Determine status based on current streak.

        Args:
            current_streak: Number of days completed this week

        Returns:
            Status string ("Active" or "Inactive")
        """
        if current_streak >= 1:
            return "Active"
        else:
            return "Inactive"
