# Habit Tracker Architecture

Written by team-lead before spawning teammates. This is the shared blueprint — teammates read it to understand what they are building and how their module fits.

## Overview

A Python CLI habit tracker that allows users to:
1. Add/manage habits
2. Log daily completions
3. View weekly streak summaries
4. Export data to CSV
5. Persist data in SQLite

## Module Structure

### Types Layer (`src/types/`)
- `models.py`: Core data types
  - `Habit`: name (str), description (str), habit_id (int), created_date (date)
  - `Completion`: habit_id (int), completion_date (date)
  - `WeeklyStreak`: habit_id (str), week_start_date (date), days_completed (int), streak_status (str)
  - `HabitExport`: habit_name (str), completed_dates (list[str]), current_streak (int)

### Config Layer (`src/config/`)
- `settings.py`: Configuration constants
  - `DB_PATH`: Path to SQLite database file (default: ~/.habit_tracker/habits.db)
  - `DEFAULT_STREAK_THRESHOLD`: Days required for streak (default: 1)
  - `WEEK_START_DAY`: Day week starts on (default: 0 = Monday)

### Repo Layer (`src/repo/`)
- `database.py`: SQLite operations
  - `HabitDB` class: connection management, schema initialization
  - Methods: `get_connection()`, `init_db()`, `close()`
- `habit_repo.py`: Habit data access
  - `HabitRepository` class
  - Methods: `create_habit(name, desc)`, `get_habit(id)`, `list_habits()`, `update_habit(id, name, desc)`, `delete_habit(id)`
- `completion_repo.py`: Completion log data access
  - `CompletionRepository` class
  - Methods: `log_completion(habit_id, date)`, `get_completions(habit_id, start_date, end_date)`, `has_completion(habit_id, date)`

### Service Layer (`src/service/`)
- `habit_service.py`: Business logic for habits
  - `HabitService` class
  - Methods: `add_habit(name, desc)`, `list_all_habits()`, `remove_habit(id)`, `get_habit_details(id)`
- `logging_service.py`: Completion logging
  - `LoggingService` class
  - Methods: `log_today(habit_id)`, `log_date(habit_id, date)`, `undo_completion(habit_id, date)`
- `streak_service.py`: Streak calculations
  - `StreakService` class
  - Methods: `get_weekly_streak(habit_id)`, `get_all_weekly_streaks()`, `calculate_streak(completions, week_start)`
- `export_service.py`: CSV export
  - `ExportService` class
  - Methods: `export_to_csv(filepath, include_habits=None)`, `prepare_export_data(habit_id)`

### Providers Layer (`src/providers/`)
- `logger.py`: Logging utilities
  - `setup_logger()`: Initialize logging
  - `log_info(msg)`, `log_error(msg)`, `log_debug(msg)`
- `date_utils.py`: Date/time helpers
  - `today()`, `get_week_start(date)`, `get_week_end(date)`, `date_range(start, end)`
- `csv_writer.py`: CSV file writing
  - `write_csv(filepath, headers, rows)`

### Runtime Layer (`src/runtime/`)
- `app.py`: Application initialization and wiring
  - `HabitTrackerApp` class
  - Methods: `initialize()`, `run()`, `shutdown()`
  - Sets up database, repositories, services

### UI Layer (`src/ui/`)
- `cli.py`: Main CLI entry point and command dispatcher
  - Command handlers:
    - `add_habit(name, description)`
    - `list_habits()`
    - `log_habit(habit_id, [date])`
    - `view_streaks([habit_id])`
    - `export(output_path, [habit_ids])`
    - `help()`
  - Usage: `python -m src.ui.cli <command> [args]`

### Utils Layer (`src/utils/`)
- `formatters.py`: Output formatting helpers
  - `format_table(rows, headers)`
  - `format_date(date)`, `parse_date_string(s)`
  - `format_streak_display(streak_data)`

### Main Entry Point
- `main.py` at repo root: Simple entry point that calls `src.runtime.app.HabitTrackerApp.run()`

## Interfaces

### Type Contracts
All modules use types from `src/types/models.py`. Every entry point (CLI input, DB results) parses data into these types.

### Repository Interface
```python
# HabitRepository
create_habit(name: str, description: str) -> Habit
get_habit(habit_id: int) -> Habit | None
list_habits() -> list[Habit]
update_habit(habit_id: int, name: str, description: str) -> None
delete_habit(habit_id: int) -> None

# CompletionRepository
log_completion(habit_id: int, date: date) -> None
get_completions(habit_id: int, start_date: date, end_date: date) -> list[Completion]
has_completion(habit_id: int, date: date) -> bool
```

### Service Interface
```python
# HabitService
add_habit(name: str, description: str) -> Habit
list_all_habits() -> list[Habit]
remove_habit(habit_id: int) -> None
get_habit_details(habit_id: int) -> Habit

# LoggingService
log_today(habit_id: int) -> None
log_date(habit_id: int, date: date) -> None
undo_completion(habit_id: int, date: date) -> None

# StreakService
get_weekly_streak(habit_id: int) -> WeeklyStreak
get_all_weekly_streaks() -> list[WeeklyStreak]

# ExportService
export_to_csv(filepath: str, include_habits: list[int] | None) -> None
```

## Shared Data Structures

### Database Schema
```sql
CREATE TABLE habits (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_date DATE NOT NULL
);

CREATE TABLE completions (
  id INTEGER PRIMARY KEY,
  habit_id INTEGER NOT NULL,
  completion_date DATE NOT NULL,
  FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
  UNIQUE(habit_id, completion_date)
);

CREATE INDEX idx_completions_habit_date ON completions(habit_id, completion_date);
```

### CSV Export Format
```
Habit,Week Starting,Days Completed,Status
Reading,2024-05-01,5,Active
Running,2024-05-01,3,Active
```

## External Dependencies

- **sqlite3** (built-in): Database operations
- **datetime** (built-in): Date/time handling
- **csv** (built-in): CSV export
- **argparse** (built-in): CLI argument parsing
- **pathlib** (built-in): File path handling
- **json** (built-in): Optional configuration storage

No external packages required.

## Layer Validation

Run `python lint.py` to verify all files respect the layer dependencies. The linter:
- Ensures every file lives in exactly one layer directory
- Validates that imports respect forward dependency direction
- Enforces 300-line file limit
- Uses Python's `ast` module for accurate import analysis

Exit code 0 = all checks pass; exit code 1 = violations found.
