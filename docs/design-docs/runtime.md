# Runtime Layer Design

## Overview

The runtime layer manages application initialization and component lifecycle. It acts as the central wiring hub that brings together all layers (types, config, repo, services, providers) and provides a single entry point for the UI layer.

The runtime layer is responsible for:
- Database initialization
- Creating all repositories and services
- Dependency injection between components
- Application lifecycle management (startup and shutdown)

## Module: app.py

### Purpose
Provides the main application class that initializes and wires together all components.

### HabitTrackerApp Class

**Responsibilities:**
- Initialize all components in dependency order
- Manage dependencies between layers
- Provide getter methods for UI layer to access services
- Clean shutdown of database connections

**Key Methods:**
- `__init__()`: Create all component instances (but don't initialize yet)
- `initialize() -> None`: Set up database schema and prepare for use
- `get_habit_service() -> HabitService`: Get habit service
- `get_logging_service() -> LoggingService`: Get logging service
- `get_streak_service() -> StreakService`: Get streak service
- `get_export_service() -> ExportService`: Get export service
- `shutdown() -> None`: Clean up resources and close connections

### Dependency Injection Pattern

The app wires dependencies in the following order:

```
1. HabitDB (raw database)
   ↓
2. HabitRepository, CompletionRepository (depend on HabitDB)
   ↓
3. Services (depend on repositories):
   - HabitService(HabitRepository)
   - LoggingService(HabitRepository, CompletionRepository)
   - StreakService(HabitRepository, CompletionRepository)
   - ExportService(HabitRepository, CompletionRepository)
```

This ensures:
- No circular dependencies
- Each component has exactly what it needs
- Easy to test (can inject mock repositories)
- Clean separation of concerns

### Usage Pattern

```python
# Initialize
app = HabitTrackerApp()
app.initialize()  # Set up database

# Use services
habit_service = app.get_habit_service()
habit = habit_service.add_habit("Reading", "30 min daily")

logging_service = app.get_logging_service()
logging_service.log_today(habit.habit_id)

streak_service = app.get_streak_service()
streak = streak_service.get_weekly_streak(habit.habit_id)

export_service = app.get_export_service()
export_service.export_to_csv("/tmp/habits.csv")

# Shutdown
app.shutdown()  # Clean up database
```

## Import Structure

The runtime layer may import from:
- `types`: Type definitions
- `config`: Configuration constants and functions
- `repo`: Database and repository classes
- `service`: Business logic services
- `providers`: Utility functions

The runtime layer must NOT import from:
- UI layer
- Any external packages

This ensures runtime can be tested independently and maintains proper layer isolation.

## Initialization Sequence

### Construction Phase (`__init__`)
1. Create HabitDB instance
2. Create HabitRepository and CompletionRepository
3. Create all service instances with their dependencies

At this point, no database operations occur - this is just object creation.

### Initialization Phase (`initialize`)
1. Ensure database directory exists (via `create_db_directory()`)
2. Initialize database schema (via `db.init_db()`)

The split between `__init__` and `initialize` allows:
- Lazy initialization (app can be created without immediately touching disk)
- Testing (can skip `initialize` for in-memory tests)
- Error handling (initialization errors can be caught separately)

### Shutdown Phase (`shutdown`)
1. Close database connection
2. All other resources are automatically cleaned up

## Error Handling

**During initialization:**
- `IOError`: Database directory or file cannot be created
- `sqlite3.Error`: Database schema initialization fails
- Both should be propagated to the caller for handling

**During operation:**
- Services raise `ValueError` for business logic errors
- Repository raises `sqlite3.IntegrityError` for constraint violations
- UI layer catches and reports these to the user

## Testing Considerations

For unit testing services, create a mock app:

```python
class MockApp:
    def __init__(self, in_memory=True):
        self._db = HabitDB()
        if in_memory:
            self._db._db_path = ":memory:"
        self._habit_repo = HabitRepository(self._db)
        self._completion_repo = CompletionRepository(self._db)
        self._db.init_db()  # Initialize in-memory schema
        
        self._habit_service = HabitService(self._habit_repo)
        self._logging_service = LoggingService(self._habit_repo, self._completion_repo)
        # ... other services
```

Then test services independently:

```python
app = MockApp()
habit_service = app.get_habit_service()
habit = habit_service.add_habit("Test", "Test habit")
assert habit.name == "Test"
app.shutdown()
```

## Dependencies

- **types**: Habit, Completion, WeeklyStreak, HabitExport
- **config**: create_db_directory, other configuration
- **repo**: HabitDB, HabitRepository, CompletionRepository
- **service**: HabitService, LoggingService, StreakService, ExportService
- **providers**: date_utils, logger, csv_writer
