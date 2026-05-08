"""
Application initialization and dependency injection wiring.

This module provides the HabitTrackerApp class which orchestrates application
lifecycle and wires all components together. It serves as the single entry point
for the entire application.
"""

from src.config.settings import create_db_directory
from src.repo.database import HabitDB
from src.repo.habit_repo import HabitRepository
from src.repo.completion_repo import CompletionRepository
from src.service.habit_service import HabitService
from src.service.logging_service import LoggingService
from src.service.streak_service import StreakService
from src.service.export_service import ExportService


class HabitTrackerApp:
    """
    Main application class for the habit tracker.

    Manages application lifecycle including initialization, component wiring,
    and cleanup. Uses dependency injection to wire repositories and services.
    All components are initialized on demand and cached as instance variables.
    """

    def __init__(self):
        """Initialize the application with uninitialized component references."""
        self._db: HabitDB | None = None
        self._habit_repo: HabitRepository | None = None
        self._completion_repo: CompletionRepository | None = None
        self._habit_service: HabitService | None = None
        self._logging_service: LoggingService | None = None
        self._streak_service: StreakService | None = None
        self._export_service: ExportService | None = None

    def initialize(self) -> None:
        """
        Initialize all application components.

        Sets up the database, creates repositories, and initializes services
        with proper dependency injection. This should be called before the
        application begins processing requests.

        Ensures:
        - Database directory exists
        - Database schema is initialized
        - All repositories are created
        - All services are wired with their dependencies
        """
        # Ensure database directory exists
        create_db_directory()

        # Initialize database
        self._db = HabitDB()
        self._db.init_db()

        # Initialize repositories
        self._habit_repo = HabitRepository(self._db)
        self._completion_repo = CompletionRepository(self._db)

        # Initialize services with dependency injection
        self._habit_service = HabitService(self._habit_repo)
        self._logging_service = LoggingService(self._completion_repo)
        self._streak_service = StreakService(self._completion_repo, self._habit_repo)
        self._export_service = ExportService(self._habit_repo, self._completion_repo)

    def get_habit_service(self) -> HabitService:
        """
        Get the HabitService instance.

        Returns:
            The initialized HabitService for managing habits

        Raises:
            RuntimeError: If application has not been initialized
        """
        if self._habit_service is None:
            raise RuntimeError(
                "Application not initialized. Call initialize() first."
            )
        return self._habit_service

    def get_logging_service(self) -> LoggingService:
        """
        Get the LoggingService instance.

        Returns:
            The initialized LoggingService for logging completions

        Raises:
            RuntimeError: If application has not been initialized
        """
        if self._logging_service is None:
            raise RuntimeError(
                "Application not initialized. Call initialize() first."
            )
        return self._logging_service

    def get_streak_service(self) -> StreakService:
        """
        Get the StreakService instance.

        Returns:
            The initialized StreakService for calculating streaks

        Raises:
            RuntimeError: If application has not been initialized
        """
        if self._streak_service is None:
            raise RuntimeError(
                "Application not initialized. Call initialize() first."
            )
        return self._streak_service

    def get_export_service(self) -> ExportService:
        """
        Get the ExportService instance.

        Returns:
            The initialized ExportService for exporting data

        Raises:
            RuntimeError: If application has not been initialized
        """
        if self._export_service is None:
            raise RuntimeError(
                "Application not initialized. Call initialize() first."
            )
        return self._export_service

    def shutdown(self) -> None:
        """
        Clean up application resources.

        Closes the database connection and resets all component references.
        Safe to call even if application was not initialized.
        """
        if self._db is not None:
            self._db.close()

        # Reset references
        self._db = None
        self._habit_repo = None
        self._completion_repo = None
        self._habit_service = None
        self._logging_service = None
        self._streak_service = None
        self._export_service = None
