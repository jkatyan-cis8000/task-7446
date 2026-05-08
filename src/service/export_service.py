"""
Business logic for exporting habit data.

This service handles the export of habit data to CSV format, gathering
completion history and streak information for specified habits.
"""

from typing import List, Optional

from src.types.models import Habit, HabitExport
from src.repo.habit_repo import HabitRepository
from src.repo.completion_repo import CompletionRepository
from src.providers.csv_writer import write_csv
from src.providers.date_utils import format_date, get_week_start, get_week_end, today


class ExportService:
    """
    Business logic service for exporting habit data.

    Provides methods for preparing habit data for export and writing it to
    CSV files in a user-friendly format.
    """

    def __init__(
        self, habit_repo: HabitRepository, completion_repo: CompletionRepository
    ):
        """
        Initialize the ExportService with repositories.

        Args:
            habit_repo: HabitRepository for retrieving habits
            completion_repo: CompletionRepository for completion data
        """
        self._habit_repo = habit_repo
        self._completion_repo = completion_repo

    def export_to_csv(
        self, filepath: str, include_habits: Optional[List[int]] = None
    ) -> None:
        """
        Export habit data to a CSV file.

        If include_habits is None, exports all habits. Otherwise exports only
        the specified habit IDs.

        The CSV includes a weekly summary with streak information for each habit.

        Args:
            filepath: Path to write the CSV file to
            include_habits: List of habit IDs to export, or None for all

        Raises:
            ValueError: If any specified habit ID doesn't exist
            IOError: If the file cannot be written
        """
        # Get habits to export
        all_habits = self._habit_repo.list_habits()

        if include_habits is None:
            habits_to_export = all_habits
        else:
            # Validate all specified habits exist
            habits_dict = {h.habit_id: h for h in all_habits}
            for habit_id in include_habits:
                if habit_id not in habits_dict:
                    raise ValueError(f"Habit with ID {habit_id} not found")
            habits_to_export = [habits_dict[hid] for hid in include_habits]

        # Prepare CSV data
        headers = ["Habit", "Week Starting", "Days Completed", "Status"]
        rows = []

        # Get current week info
        current_date = today()
        week_start = get_week_start(current_date)

        for habit in habits_to_export:
            export_data = self.prepare_export_data(habit.habit_id)
            rows.append(
                [
                    export_data.habit_name,
                    format_date(week_start),
                    str(len(export_data.completed_dates)),
                    "Active" if export_data.current_streak > 0 else "Inactive",
                ]
            )

        # Write to CSV
        write_csv(filepath, headers, rows)

    def prepare_export_data(self, habit_id: int) -> HabitExport:
        """
        Prepare habit data for export.

        Gathers the habit name and all completion dates in the current week,
        calculating the current streak.

        Args:
            habit_id: The ID of the habit to prepare

        Returns:
            A HabitExport object with export-ready data

        Raises:
            ValueError: If the habit doesn't exist
        """
        # Get habit
        habit = self._habit_repo.get_habit(habit_id)
        if habit is None:
            raise ValueError(f"Habit with ID {habit_id} not found")

        # Get current week boundaries
        current_date = today()
        week_start = get_week_start(current_date)
        week_end = get_week_end(current_date)

        # Get completions for current week
        completions = self._completion_repo.get_completions(
            habit_id, week_start, week_end
        )

        # Format completion dates as strings
        completed_dates = sorted(
            [format_date(c.completion_date) for c in completions]
        )

        # Calculate streak (days completed in current week)
        current_streak = len(set(c.completion_date for c in completions))

        return HabitExport(
            habit_name=habit.name,
            completed_dates=completed_dates,
            current_streak=current_streak,
        )
