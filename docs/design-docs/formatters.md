# Utils Layer: Output Formatters

## Overview

The `src/utils/formatters.py` module provides pure, stateless formatting utilities for converting Python objects to human-readable strings displayed by the CLI. These functions have no domain logic, no external dependencies, and no cross-layer imports.

## Design Principles

1. **Pure Functions**: All functions are stateless and deterministic. Given the same input, they always produce the same output.
2. **No Domain Logic**: Formatters only handle presentation, not business logic.
3. **Type Validation**: All functions validate input types and raise descriptive errors on invalid input.
4. **Single Responsibility**: Each function has exactly one formatting concern.

## Functions

### `format_date(d: date) -> str`

Formats a date object as an ISO 8601 string (YYYY-MM-DD).

**Constraints**:
- Input must be a Python `datetime.date` object
- Output is always YYYY-MM-DD format
- Raises `TypeError` if input is not a date

**Usage**:
```python
from datetime import date
format_date(date(2024, 5, 1))  # "2024-05-01"
```

### `parse_date_string(s: str) -> date`

Parses a date string in YYYY-MM-DD format and returns a date object.

**Constraints**:
- Input must be a string in YYYY-MM-DD format
- Whitespace is not trimmed; input must be exactly formatted
- Raises `ValueError` if format is invalid
- Raises `TypeError` if input is not a string

**Usage**:
```python
parse_date_string("2024-05-01")  # date(2024, 5, 1)
```

### `format_table(headers: List[str], rows: List[List[str]]) -> str`

Formats a table with headers and data rows as a fixed-width ASCII table.

**Constraints**:
- `headers` must be a non-empty list of strings
- `rows` must be a list of lists, where each inner list has exactly as many elements as `headers`
- All cell values must be strings
- Column widths are automatically calculated based on header and cell content
- Columns are separated by two spaces
- A separator line of dashes is inserted between headers and data rows

**Raises**:
- `TypeError` if headers/rows are not lists or contain non-string values
- `ValueError` if rows have inconsistent column counts or if headers is empty

**Usage**:
```python
headers = ["Habit", "Days Completed", "Status"]
rows = [
    ["Reading", "5", "Active"],
    ["Running", "3", "Active"],
]
print(format_table(headers, rows))
# Output:
# Habit     Days Completed  Status
# -------   ---------------  ------
# Reading   5                Active
# Running   3                Active
```

### `format_streak_display(habit_name: str, days_completed: int, status: str) -> str`

Pretty prints streak information for a single habit.

**Constraints**:
- `habit_name` must be a non-empty string
- `days_completed` must be a non-negative integer
- `status` must be a non-empty string
- Uses a symbolic indicator: "✓" for "Active" status, "○" for others
- Automatically pluralizes "day/days" based on count
- Case-insensitive status comparison for symbol selection

**Usage**:
```python
format_streak_display("Reading", 5, "Active")
# "✓ Reading: 5 days (Active)"

format_streak_display("Running", 1, "Active")
# "✓ Running: 1 day (Active)"

format_streak_display("Yoga", 0, "Inactive")
# "○ Yoga: 0 days (Inactive)"
```

## Implementation Notes

1. **Column Alignment**: `format_table` left-aligns all cells for consistency and readability.
2. **Unicode Symbols**: The streak display uses standard Unicode box-drawing characters (✓ and ○) for visual clarity.
3. **Error Messages**: All validation errors provide clear, actionable messages to help debugging.
4. **Date Format**: Consistently uses ISO 8601 (YYYY-MM-DD) format throughout to avoid ambiguity across locales.

## Testing Considerations

- Test with empty tables (headers only)
- Test with tables of varying column widths
- Test date parsing with invalid formats (e.g., "05-01-2024", "2024/05/01")
- Test format_streak_display with edge cases (0 days, 1 day, large numbers)
- Test with special characters in habit names
