# Types Layer Design

## Overview

The types layer defines the core data structures used throughout the habit tracker application. These are pure type definitions with no business logic, serving as the single source of truth for data shape across all layers.

All types are implemented as Python dataclasses with:
- Field validation in `__post_init__`
- Custom `__repr__` methods for debugging
- Type annotations for IDE support and mypy compatibility

## Design Philosophy

**Pure Types, No Logic**
- No methods beyond `__init__`, `__post_init__`, and `__repr__`
- No imports from other internal modules (only `datetime` and `typing`)
- Validation only, no business operations
- Safe to use anywhere in the codebase without circular dependencies

**Single Responsibility**
- Each type represents one concept (Habit, Completion, WeeklyStreak, HabitExport)
- Types are immutable after creation (dataclass frozen=False by default, but not modified by design)
- Field names match database columns and external APIs

## Types

### Habit

Represents a habit that a user wants to track.

```python
@dataclass
class Habit:
    name: str              # Unique identifier
    description: str       # Optional description
    habit_id: int         # Database-assigned ID
    created_date: date    # When the habit was created
```

**Validation:**
- `name`: Must be non-empty string
- `description`: Must be string (can be empty)
- `habit_id`: Must be positive integer
- `created_date`: Must be a `datetime.date` object

**Usage:**
- Created by `HabitRepository.create_habit()`
- Returned by all habit query methods
- Passed to service layer for business logic

**Example:**
```python
habit = Habit(
    name="Reading",
    description="30 minutes daily",
    habit_id=1,
    created_date=date(2026, 5, 8)
)
```

### Completion

Represents a single completion of a habit on a specific date.

```python
@dataclass
class Completion:
    habit_id: int           # Which habit was completed
    completion_date: date   # When it was completed
```

**Validation:**
- `habit_id`: Must be positive integer
- `completion_date`: Must be a `datetime.date` object

**Usage:**
- Created by `CompletionRepository.log_completion()`
- Returned by `CompletionRepository.get_completions()`
- Used by `StreakService` for streak calculations

**Example:**
```python
completion = Completion(
    habit_id=1,
    completion_date=date(2026, 5, 8)
)
```

### WeeklyStreak

Represents a weekly summary of habit completions.

```python
@dataclass
class WeeklyStreak:
    habit_id: str          # Habit identifier (as string for compatibility)
    week_start_date: date  # Monday of the week
    days_completed: int    # Number of days completed in the week
    streak_status: str     # Status: "Active", "Inactive", etc.
```

**Validation:**
- `habit_id`: Must be non-empty string
- `week_start_date`: Must be a `datetime.date` object
- `days_completed`: Must be non-negative integer
- `streak_status`: Must be non-empty string

**Usage:**
- Created by `StreakService.get_weekly_streak()`
- Returned by `StreakService.get_all_weekly_streaks()`
- Passed to UI formatters for display

**Example:**
```python
streak = WeeklyStreak(
    habit_id="1",
    week_start_date=date(2026, 5, 5),  # Monday
    days_completed=5,
    streak_status="Active"
)
```

### HabitExport

Represents habit data formatted for CSV export.

```python
@dataclass
class HabitExport:
    habit_name: str              # Name of the habit
    completed_dates: List[str]   # Dates as ISO format strings
    current_streak: int          # Current streak count
```

**Validation:**
- `habit_name`: Must be non-empty string
- `completed_dates`: Must be list of strings (ISO format)
- `current_streak`: Must be non-negative integer

**Usage:**
- Created by `ExportService.prepare_export_data()`
- Consumed by `ExportService.export_to_csv()`
- Contains data ready for CSV output

**Example:**
```python
export = HabitExport(
    habit_name="Reading",
    completed_dates=["2026-05-01", "2026-05-02", "2026-05-03"],
    current_streak=3
)
```

## Design Decisions

### 1. Dataclasses vs NamedTuple

**Choice:** Dataclasses

**Rationale:**
- Mutable by default (allows flexibility if needed)
- Better repr and easier field documentation
- More extensible if validation logic evolves
- Better IDE support and type checking

### 2. Validation Strategy

**Approach:** Strict validation in `__post_init__`

**Rationale:**
- Fail fast on invalid data
- Prevent invalid states from propagating
- Clear error messages for debugging
- Type safety enforced at runtime

### 3. Date Representation

**Approach:** Use `datetime.date` everywhere

**Rationale:**
- Standard Python library, no external dependencies
- ISO format string conversion handled by date layer
- SQLite date conversion in repository layer
- UI formatters handle presentation

**Implementation Note:** Repository layer handles conversion from SQLite strings to date objects in `_row_to_habit()` and `_row_to_completion()` using `date.fromisoformat()`.

### 4. ID Representation

**Inconsistency Note:** 
- `Habit.habit_id` is `int` (database ID)
- `WeeklyStreak.habit_id` is `str` (for compatibility)

**Rationale:** 
- `Habit` comes from database, naturally uses int
- `WeeklyStreak` is constructed by service layer for display
- String allows flexibility in export/display contexts
- Service layer handles conversion between the two

### 5. List Representation

**Choice:** `List[str]` for `HabitExport.completed_dates`

**Rationale:**
- Already in display format (ISO strings)
- Ready for CSV output
- No conversion needed by export service
- Simplifies CSV writing logic

## Import Guidelines

The types layer may import from:
- `dataclasses`: Type definition support
- `datetime`: Date objects
- `typing`: Type annotations (List, Optional, etc.)

Types must NOT import from:
- Any internal modules (config, repo, service, etc.)
- External packages

This ensures zero circular dependencies and maximum reusability.

## Usage Patterns

### In Repositories
```python
# Creating types from database rows
habit = Habit(
    name=row["name"],
    description=row["description"],
    habit_id=row["id"],
    created_date=date.fromisoformat(row["created_date"])
)
```

### In Services
```python
# Using types from repositories
habits = habit_repo.list_habits()
for habit in habits:
    print(f"Habit: {habit.name} (ID: {habit.habit_id})")
```

### In UI/Export
```python
# Types ready for formatting
streaks = streak_service.get_all_weekly_streaks()
for streak in streaks:
    display = format_streak_display(
        streak.habit_id,
        streak.days_completed,
        streak.streak_status
    )
```

## Testing Considerations

Types are easily testable:

```python
# Valid construction
habit = Habit("Reading", "Daily", 1, date.today())

# Invalid construction raises ValueError
with pytest.raises(ValueError):
    habit = Habit("", "", -1, "2026-05-08")  # Multiple violations
```

## Future Extensions

If the application grows:
- Add optional fields: `@dataclass` supports default values
- Add computed properties: Add methods while keeping core immutable
- Add serialization: `asdict()` and JSON encoding support

The current design supports these extensions without breaking existing code.

## Dependencies

- **dataclasses** (built-in): Type definitions
- **datetime** (built-in): Date objects
- **typing** (built-in): Type annotations
