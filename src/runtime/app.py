"""
Application initialization and dependency wiring.

This module initializes the entire application stack, setting up the database,
repositories, and services with proper dependency injection. It provides a
single entry point for the UI layer to access all application functionality.
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

    Initializes and manages all components of the application, including
    database connection, repositories, and services. Provides a clean interface
    for the UI layer to access application functionality.

    Uses dependency injection to pass repositories and services to each layer,
    ensuring loose coupling and testability.
    """

    def __init__(self):
        """Initialize the application instance."""
        # Core components (uninitialized)
        self._db: HabitDB = HabitDB()
        self._habit_repo: HabitRepository = HabitRepository(self._db)
        self._completion_repo: CompletionRepository = CompletionRepository(self._db)

        # Services (uninitialized)
        self._habit_service: HabitService = HabitService(self._habit_repo)
        self._logging_service: LoggingService = LoggingService(
            self._habit_repo, self._completion_repo
        )
        self._streak_service: StreakService = StreakService(
            self._habit_repo, self._completion_repo
        )
        self._export_service: ExportService = ExportService(
            self._habit_repo, self._completion_repo
        )

    def initialize(self) -> None:
        """
        Initialize the application.

        Sets up the database schema and ensures all components are ready to use.
        This must be called before any other operations.

        Raises:
            IOError: If the database cannot be created or initialized
        """
        # Ensure database directory exists
        create_db_directory()

        # Initialize the database schema
        self._db.init_db()

    def get_habit_service(self) -> HabitService:
        """
        Get the habit service for habit management operations.

        Returns:
            The HabitService instance
        """
        return self._habit_service

    def get_logging_service(self) -> LoggingService:
        """
        Get the logging service for completion logging operations.

        Returns:
            The LoggingService instance
        """
        return self._logging_service

    def get_streak_service(self) -> StreakService:
        """
        Get the streak service for streak calculation operations.

        Returns:
            The StreakService instance
        """
        return self._streak_service

    def get_export_service(self) -> ExportService:
        """
        Get the export service for exporting habit data.

        Returns:
            The ExportService instance
        """
        return self._export_service

    def shutdown(self) -> None:
        """
        Shut down the application cleanly.

        Closes the database connection and cleans up resources.
        Should be called before application exit.
        """
        self._db.close()
