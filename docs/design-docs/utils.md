# Utils Layer Design

## Overview

The utils layer provides pure formatting and parsing utilities with no domain logic or internal imports. It exists solely to support user-facing output formatting and input parsing. The utils layer can ONLY import from `utils` modules.

## Module: formatters.py

### Purpose
Provides formatting functions for CLI output and parsing utilities for user input. All functions are pure (no side effects, deterministic).

### Key Functions

#### `format_table(headers, rows) -> str`
Formats a list of rows into a nicely aligned ASCII table.
- **Parameters**: 
  - headers: List of column header strings
  - rows: List of rows, each row is a list of strings
- **Returns**: Formatted table as a string with box drawing characters
- **Behavior**: 
  - Calculates column widths based on header and content
  - Creates horizontal separators with `+` and `-`
  - Aligns cells with left justification
  - Each row is surrounded by `|` characters
- **Validation**: Raises ValueError if headers empty or row lengths don't match headers

#### `format_date(d) -> str`
Formats a date object to ISO format string (YYYY-MM-DD).
- **Parameters**: d: A date object
- **Returns**: String in format YYYY-MM-DD
- **Error Handling**: Raises TypeError if input is not a date object
- **Note**: This is a pure wrapper around strftime for consistency

#### `parse_date_string(s) -> date`
Parses a date string in ISO format (YYYY-MM-DD) to a date object.
- **Parameters**: s: A date string
- **Returns**: Parsed date object
- **Error Handling**: Raises ValueError if format is invalid, TypeError if input is not a string
- **Note**: Manual parsing avoids dependency on strptime quirks; more robust for different platforms

#### `format_streak_display(habit_name, days_completed, status) -> str`
Formats a streak summary with visual progress bar.
- **Parameters**:
  - habit_name: Name of the habit (string)
  - days_completed: Days completed in week (int, 0-7)
  - status: Streak status like "Active" or "Inactive" (string)
- **Returns**: Multi-line formatted string with progress bar
- **Output Format**:
  ```
  Habit Name: X/7 days
    [████░░░]
    Status: Active
  ```
- **Progress Bar**: Uses `█` (filled) and `░` (empty) characters for visualization

### Helper Functions

#### `_format_table_rows(headers, rows) -> str`
Internal function that builds the formatted table structure.

#### `_build_progress_bar(days_completed, width) -> str`
Internal function that creates the progress bar visualization.

## Design Decisions

### Pure Functions Only
- No module-level state or side effects
- All functions are deterministic (same input always produces same output)
- No imports from other src layers (only built-in modules)
- This ensures formatters can be tested in isolation and used anywhere

### Date Formatting Consistency
- ISO format (YYYY-MM-DD) is used throughout
- This format is:
  - Unambiguous across locales
  - Compatible with ISO 8601 standard
  - Sortable as strings
  - Easy to parse and validate

### ASCII Table Design
- Uses box-drawing characters (`+`, `-`, `|`) for clear visual boundaries
- Left-aligns text for readability
- Calculates column widths dynamically based on content
- Provides both header and bottom separators for clarity

### Progress Bar Visualization
- 7 characters wide (representing 7 days of the week)
- Filled blocks (`█`) show completed days
- Empty blocks (`░`) show remaining days
- Makes streak progress immediately obvious

### String Validation
- All functions validate input types
- Raises clear, specific errors (TypeError vs ValueError)
- Input coercion is avoided to catch programming errors

## Integration Notes

### With CLI Layer
- formatters will be imported by `src.ui.cli` to display tables and streak information
- format_date will be used for consistent date display
- format_streak_display will show weekly summaries

### With Other Layers
- Parse_date_string might be used by CLI to parse user input dates
- Formatters are display-only and don't modify data

## Testing Considerations

Key test scenarios:
- Empty tables (header-only)
- Tables with varying column widths
- Edge cases for date parsing (leap years, month boundaries)
- Progress bar for 0 and 7 completed days
- Proper alignment with multi-character unicode in progress bar

## Constraints and Assumptions

1. **ISO Format Only**: All date strings must be in YYYY-MM-DD format
2. **String Values**: Table formatting expects all cells to be strings (no automatic conversion)
3. **English Output**: Status strings and labels are in English
4. **7-Day Week**: Progress bar assumes a 7-day week structure
5. **ASCII/UTF-8**: Output assumes UTF-8 capable terminal for box-drawing and progress bar characters
