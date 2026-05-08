# Repository Layer Design

## Overview

The repository layer implements data access logic for the habit tracker. It provides a clean separation between the database implementation details and business logic, ensuring that the rest of the application works with type-safe objects rather than raw database rows.

The layer manages:
- SQLite connection lifecycle
- Database schema initialization
- CRUD operations for habits
- Completion log storage and querying

All database operations return objects from `src/types/models.py` (Habit, Completion).

## Architecture

```
┌─────────────────────────────────┐
│   Service Layer (business logic)│
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│ Repository Layer (data access) │
│  ├─ HabitRepository            │
│  └─ CompletionRepository       │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   HabitDB (connection mgmt)    │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│    SQLite Database File         │
└─────────────────────────────────┘
```

## Module: database.py

### Purpose
Manages SQLite database connections and schema initialization.

### HabitDB Class

**Responsibilities:**
- Establish and maintain database connections
- Initialize database schema on first use
- Provide connection access to repository classes
- Clean shutdown of connections

**Key Methods:**
- `__init__()`: Initialize database manager
- `get_connection() -> sqlite3.Connection`: Get or create connection
- `init_db() -> None`: Create schema (idempotent)
- `close() -> None`: Close connection

### Schema

**habits table:**
```sql
CREATE TABLE habits (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_date DATE NOT NULL
);
```

**completions table:**
```sql
CREATE TABLE completions (
  id INTEGER PRIMARY KEY,
  habit_id INTEGER NOT NULL,
  completion_date DATE NOT NULL,
  FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
  UNIQUE(habit_id, completion_date)
);

CREATE INDEX idx_completions_habit_date
ON completions(habit_id, completion_date);
```

### Design Decisions

1. **Connection Pooling**: Single connection per HabitDB instance
   - Simplicity: No complex pool management
   - SQLite handles concurrent reads naturally
   - Writes serialize at the database level
   - Suitable for CLI application with single user

2. **Row Factory**: Uses `sqlite3.Row` for convenient dict-like access
   - Enables column access by name: `row["habit_id"]`
   - Repositories use this to construct typed objects

3. **Foreign Keys**: Explicitly enabled with `PRAGMA foreign_keys = ON`
   - Ensures referential integrity
   - CASCADE delete removes completions when habit is deleted

4. **Schema Initialization**: Idempotent `init_db()` method
   - Can be called multiple times safely
   - Uses `CREATE TABLE IF NOT EXISTS`
   - Safe for runtime initialization in app startup

## Module: habit_repo.py

### Purpose
Provides data access operations for habits.

### HabitRepository Class

**Responsibilities:**
- CRUD operations on habits
- Translate database rows to Habit objects
- Enforce business constraints at database level

**Public Methods:**
- `create_habit(name: str, description: str) -> Habit`
- `get_habit(habit_id: int) -> Habit | None`
- `list_habits() -> List[Habit]`
- `update_habit(habit_id: int, name: str, description: str) -> None`
- `delete_habit(habit_id: int) -> None`

### Design Decisions

1. **Dependencies**: Takes HabitDB in constructor
   - Enables dependency injection
   - Repositories can be tested with mock databases
   - Single database instance can serve multiple repositories

2. **Type Safety**: All methods return Habit objects
   - `_row_to_habit()` helper converts rows to types
   - Service layer never sees raw database rows
   - Type system enforces correct usage

3. **ID Management**: 
   - Database assigns IDs (INTEGER PRIMARY KEY autoincrement)
   - `create_habit()` returns the created Habit with assigned ID
   - Clients don't need to manually manage IDs

4. **Name Uniqueness**: 
   - Database enforces via UNIQUE constraint
   - Raises `sqlite3.IntegrityError` if duplicate
   - Service layer catches and handles appropriately

5. **Deletion with Cascade**:
   - `delete_habit()` leverages foreign key CASCADE
   - Automatically removes all completions for the habit
   - No orphaned records possible

## Module: completion_repo.py

### Purpose
Provides data access operations for habit completions.

### CompletionRepository Class

**Responsibilities:**
- Log habit completions
- Query completion history
- Translate database rows to Completion objects

**Public Methods:**
- `log_completion(habit_id: int, completion_date: date) -> None`
- `get_completions(habit_id: int, start_date: date, end_date: date) -> List[Completion]`
- `has_completion(habit_id: int, completion_date: date) -> bool`

### Design Decisions

1. **Idempotent Logging**:
   - Uses `INSERT OR IGNORE` to handle duplicate completions gracefully
   - Logging the same habit on the same date is a no-op (not an error)
   - Simplifies client code (no need to check first)

2. **Date Range Queries**:
   - `get_completions()` includes both start and end dates
   - Used by streak calculations for week boundaries
   - Index on (habit_id, completion_date) optimizes these queries

3. **Efficient Existence Check**:
   - `has_completion()` uses `LIMIT 1` for fast boolean result
   - Avoids fetching full row when only checking presence
   - Used by logging service to check for existing entries

4. **Type Safety**:
   - `_row_to_completion()` helper constructs Completion objects
   - Service layer works with typed objects only

## Import Guidelines

The repository layer may import from:
- `sqlite3`: Database operations
- `datetime`: Date handling
- `src.types`: Type definitions (Habit, Completion)
- `src.config`: Configuration (DB_PATH)
- `src.repo`: Other repository classes

Repository must NOT import from:
- Service layer
- Runtime layer
- UI layer
- Providers layer (only config)

This ensures repositories remain pure data access with no business logic.

## Error Handling

**sqlite3.IntegrityError** exceptions:
- Duplicate habit names: Raised by `create_habit()` and `update_habit()`
- Foreign key violations: Raised by `log_completion()` if habit doesn't exist
- Service layer catches and converts to domain errors

**Other database errors:**
- Connection errors: Propagated (fatal errors in CLI)
- Disk full, permissions: Propagated (application should handle gracefully)

## Testing Considerations

Mock implementations of HabitDB can be created for unit testing:
```python
class MockHabitDB:
    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(":memory:")
    
    def init_db(self) -> None:
        # Initialize in-memory database for testing
        pass
    
    def close(self) -> None:
        pass
```

Repositories are then tested by injecting the mock database.

## Dependencies

- **sqlite3** (built-in): Database operations
- **datetime** (built-in): Date handling
- **src.types**: Type definitions
- **src.config**: Database configuration
