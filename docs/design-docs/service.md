# Service Layer Design

## Overview

The service layer implements business logic for the habit tracker application. It provides an abstraction between the UI and data layers, ensuring all business rules are centralized and reusable. The service layer imports from `types`, `config`, `repo`, `providers`, and other `service` modules.

## Module: habit_service.py

### Purpose
Provides business logic for managing habits (create, retrieve, list, update, delete).

### Key Classes and Methods
- `HabitService` class
  - `__init__(habit_repo)`: Initialize with repository dependency
  - `add_habit(name, description) -> Habit`: Create a new habit with validation
  - `list_all_habits() -> list[Habit]`: Retrieve all habits
  - `get_habit_details(habit_id) -> Habit`: Get a specific habit with error handling
  - `remove_habit(habit_id) -> None`: Delete a habit and its completions

### Design Decisions
- Uses dependency injection to receive HabitRepository
- Validates input parameters (name, description, habit_id) before delegating to repository
- Raises ValueError for invalid inputs, LookupError for missing habits
- Delegates all data access to repository layer
- Works exclusively with Habit type objects

### Constraints
- Habit names must be unique (enforced by database)
- Deleting a habit cascades to delete all completions
- All returned data is typed as Habit objects for type safety

## Module: logging_service.py

### Purpose
Provides business logic for logging and managing habit completions.

### Key Classes and Methods
- `LoggingService` class
  - `__init__(completion_repo)`: Initialize with repository dependency
  - `log_today(habit_id) -> None`: Log a completion for today
  - `log_date(habit_id, date) -> None`: Log a completion for a specific date
  - `undo_completion(habit_id, date) -> None`: Remove a logged completion

### Design Decisions
- `log_today()` is a convenience method that delegates to `log_date()`
- Uses `today()` from date_utils provider for testability
- Validates habit_id and date parameters before operations
- Direct database access for undo operations (no dedicated repository method)
- Ignores duplicate completions for same habit/date (enforced by UNIQUE constraint)

### Constraints
- Cannot log completions for non-existent habits (foreign key constraint)
- Same habit can only have one completion per date (UNIQUE constraint)
- Dates must be date objects, not strings

## Module: streak_service.py

### Purpose
Calculates and provides weekly streak information for habits.

### Key Classes and Methods
- `StreakService` class
  - `__init__(completion_repo, habit_repo)`: Initialize with both repositories
  - `get_weekly_streak(habit_id) -> WeeklyStreak`: Get streak for current week
  - `get_all_weekly_streaks() -> list[WeeklyStreak]`: Get streaks for all habits
  - `calculate_streak(completions, week_start) -> int`: Helper to count completions in a week

### Design Decisions
- Calculates streaks only for the current week (based on today's date)
- Week calculation respects `WEEK_START_DAY` configuration
- Streak status is "Active" if days_completed >= DEFAULT_STREAK_THRESHOLD, else "Inactive"
- `calculate_streak()` is a static helper method for reusability
- Returns WeeklyStreak type objects with habit_id as string (for compatibility)

### Constraints
- Can only calculate streaks for existing habits (raises LookupError)
- Week always starts on the configured WEEK_START_DAY and ends 6 days later
- Days completed count includes all dates with at least one completion per day

## Module: export_service.py

### Purpose
Handles exporting habit data to CSV format with completion history and streaks.

### Key Classes and Methods
- `ExportService` class
  - `__init__(habit_repo, completion_repo)`: Initialize with both repositories
  - `export_to_csv(filepath, include_habits=None) -> None`: Write habit data to CSV
  - `prepare_export_data(habit_id) -> HabitExport`: Prepare data for single habit
  - `_get_current_week_start()`: Get formatted current week start date
  - `_get_current_week_completion_count(habit_id)`: Count completions this week
  - `_get_status(current_streak)`: Determine Active/Inactive status

### Design Decisions
- CSV export includes: Habit name, week start date, days completed, status
- `include_habits=None` exports all habits; specific list filters by ID
- Completion dates in HabitExport are strings in ISO format (YYYY-MM-DD)
- Status is "Active" if current_streak >= 1, else "Inactive"
- All data is prepared as strings before CSV writing
- Uses csv_writer provider for file operations

### Constraints
- Only exports habits that exist in the database
- CSV headers and row format fixed per ARCHITECTURE.md
- All cells must be strings (dates formatted as ISO strings)
- Output directory is created automatically by csv_writer

## Integration Notes

### With Repository Layer
- All services depend on one or more repositories for data access
- Services validate business logic while repos handle data persistence
- Services transform type objects, repos handle SQL

### With Provider Layer
- HabitService: No provider dependencies
- LoggingService: Uses `today()` from date_utils
- StreakService: Uses `get_week_start()`, `get_week_end()`, `today()` from date_utils
- ExportService: Uses csv_writer, date formatting utilities

### With Configuration
- DEFAULT_STREAK_THRESHOLD used by StreakService to determine Active status
- WEEK_START_DAY used (via date_utils) for week calculation

### With Runtime Layer
- All four services are instantiated and wired by HabitTrackerApp
- Services are accessed through app methods (get_habit_service(), etc.)

## Error Handling

Services raise these exceptions:
- `ValueError`: Invalid input (non-positive IDs, invalid strings, wrong types)
- `LookupError`: Resource not found (habit doesn't exist)
- `sqlite3.IntegrityError`: Database constraint violations (duplicate names, foreign key)
- `IOError`: File write failures (from csv_writer)

## Testing Considerations

When testing service modules:
- Mock or use real repositories depending on test scope
- Services should validate inputs before calling repositories
- Static helper methods (like calculate_streak) should be unit-testable
- Week calculation should be tested for boundary conditions (week transitions)
- CSV export should create valid CSV with all habits or filtered subsets
