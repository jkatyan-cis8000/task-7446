# Providers Layer Design

## Overview

The providers layer implements cross-cutting concerns that are used throughout the application. It includes logging setup, date/time utilities, and CSV file writing capabilities. The providers layer can import from `types`, `config`, `utils`, and other `providers` modules.

## Module: logger.py

### Purpose
Provides centralized logging setup and utility functions for the entire application.

### Key Functions
- `setup_logger(name)`: Initialize and configure a logger with console output
- `get_logger(name)`: Get or create a logger instance (singleton pattern)
- `log_info(msg)`: Log info-level messages
- `log_error(msg)`: Log error-level messages
- `log_debug(msg)`: Log debug-level messages

### Design Decisions
- Uses Python's built-in `logging` module for simplicity and reliability
- Implements a singleton pattern via module-level state to avoid multiple handler registrations
- Console output streams to stdout for CLI applications
- Includes timestamp, logger name, level, and message in formatted output

## Module: date_utils.py

### Purpose
Provides utilities for date manipulation and formatting, with specific focus on week calculations based on configurable week start day.

### Key Functions
- `today()`: Returns the current date
- `get_week_start(date)`: Returns the first day of the week for a given date (respects WEEK_START_DAY config)
- `get_week_end(date)`: Returns the last day of the week for a given date
- `date_range(start, end)`: Returns a list of dates from start to end (inclusive)
- `parse_date_string(s)`: Parses ISO format date strings (YYYY-MM-DD)
- `format_date(date)`: Formats dates as ISO format strings (YYYY-MM-DD)

### Design Decisions
- Uses Python's `datetime` module for all date operations
- Week calculations respect the `WEEK_START_DAY` configuration (0=Monday, 6=Sunday)
- All date strings use ISO format (YYYY-MM-DD) for consistency and international compatibility
- Week calculation uses modulo arithmetic to handle wrap-around from Sunday to Monday

### Constraints
- Date objects are always `datetime.date`, never `datetime.datetime`
- String representations are always ISO format for consistency
- Week calculations assume 7-day weeks

## Module: csv_writer.py

### Purpose
Provides utilities for writing data to CSV files with automatic directory creation.

### Key Functions
- `write_csv(filepath, headers, rows)`: Write headers and rows to a CSV file

### Design Decisions
- Uses Python's built-in `csv` module for standard CSV generation
- Automatically creates parent directories if they don't exist (via pathlib)
- Uses UTF-8 encoding for proper character support
- Validates headers and rows before writing (all must be strings)
- Ensures row lengths match header lengths

### Error Handling
- Raises `ValueError` if headers/rows are invalid
- Raises `IOError` if file writing fails

### Constraints
- All cells must be strings (no automatic type conversion)
- CSV dialect is default (comma-separated, CRLF line endings on Windows)

## Integration Notes

### With Configuration
- `date_utils.py` imports `WEEK_START_DAY` from `src.config.settings` to enable configurable week start days
- This allows different locales to have different week start expectations

### With Other Layers
- **Service layer** will use date_utils for week calculations in streak service
- **Export service** will use csv_writer to export habit data
- **All layers** may use logger for debugging and info messages

## Testing Considerations

When testing provider modules:
- Logger setup is idempotent (can be called multiple times)
- Date calculations should be verified for week boundaries (especially week start day)
- CSV writing should create directories as needed
- All date parsing/formatting should be reversible (parse(format(date)) == date)
