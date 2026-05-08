# Runtime Layer Design

## Overview

The runtime layer manages application lifecycle and dependency injection. The `HabitTrackerApp` class serves as the single entry point for all application functionality, wiring all components together and providing accessors for use by the UI layer.

## Module: app.py

### Purpose
Provides the `HabitTrackerApp` class that orchestrates application initialization, component wiring, and cleanup.

### Key Classes and Methods

#### HabitTrackerApp class
- `__init__()`: Initialize with uninitialized component references
- `initialize() -> None`: Set up all components and wire dependencies
- `get_habit_service() -> HabitService`: Get the habit service accessor
- `get_logging_service() -> LoggingService`: Get the logging service accessor
- `get_streak_service() -> StreakService`: Get the streak service accessor
- `get_export_service() -> ExportService`: Get the export service accessor
- `shutdown() -> None`: Clean up resources and reset component references

### Design Decisions

#### Lazy vs. Eager Initialization
- Components are initialized eagerly in `initialize()` method
- This ensures all dependencies are met before any service is used
- Failing early (during initialize) is better than failing later

#### Dependency Injection Pattern
- Services receive their dependencies through constructor injection
- Repositories receive the HabitDB instance
- This makes dependencies explicit and testable

#### Service Accessors
- Services are accessed through getter methods (get_*_service)
- Getters validate that initialize() was called first
- Raises RuntimeError if accessed before initialization

#### Component Lifecycle
- Components are stored as optional instance variables (initialized to None)
- `initialize()` creates and wires all components
- `shutdown()` closes connections and resets all references
- Allows multiple initialize/shutdown cycles

### Component Wiring Order
1. Database directory creation
2. HabitDB initialization with schema
3. Repository instantiation (HabitRepository, CompletionRepository)
4. Service instantiation with repository dependencies:
   - HabitService(habit_repo)
   - LoggingService(completion_repo)
   - StreakService(completion_repo, habit_repo)
   - ExportService(habit_repo, completion_repo)

### Constraints
- All services must be accessed via getter methods (not created directly)
- Services cannot be used until `initialize()` has been called
- Each getter raises RuntimeError if called before initialization
- Shutdown is safe to call multiple times (idempotent)

## Integration Notes

### With Configuration Layer
- Uses `create_db_directory()` from config.settings
- Ensures database directory exists before opening connection

### With Repository Layer
- Creates HabitDB and passes it to repositories
- Ensures all database operations use the same connection
- Relies on repository interfaces for data access

### With Service Layer
- Wires all four services with their repository dependencies
- Services depend on repositories, not on each other
- Services are used exclusively through HabitTrackerApp accessors

### With UI Layer
- CLI creates a HabitTrackerApp instance
- CLI calls initialize() before processing commands
- CLI calls get_*_service() to access business logic
- CLI calls shutdown() during cleanup

## Error Handling

- `RuntimeError`: Raised if services are accessed before `initialize()` is called
- Database errors are propagated from HabitDB
- Repository and service errors are propagated to caller

## Testing Considerations

When testing the runtime layer:
- Create a test HabitTrackerApp instance
- Call `initialize()` before running tests
- Call `shutdown()` during cleanup
- Mock repositories if testing runtime in isolation
- Integration tests should use real repositories/database
