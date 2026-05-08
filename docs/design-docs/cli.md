# UI Layer: Command Line Interface

## Overview

The `src/ui/cli.py` and `src/ui/commands.py` modules provide the complete command-line interface for the habit tracker. The architecture separates concerns:

- **cli.py**: Argument parsing, command dispatch, and application lifecycle management
- **commands.py**: Individual command handlers with business logic calls and output formatting

## Design Principles

1. **Single Responsibility**: Each command handler focuses on one operation
2. **Error Handling**: Graceful error handling with informative user messages
3. **Clean Dispatch**: Argument parsing drives command dispatch
4. **Layered Access**: Commands access services through HabitTrackerApp dependency injection

## Module Structure

### cli.py: Main Entry Point (108 lines)

**Responsibilities**:
- Parse command-line arguments using argparse
- Create and initialize HabitTrackerApp
- Dispatch to appropriate command handler
- Handle application shutdown and cleanup
- Provide unified error handling

**Key Function**:
```python
def main(argv: Optional[List[str]] = None) -> None
```

Accepts command-line arguments, parses them, initializes the app, and dispatches to the appropriate handler. Always calls `app.shutdown()` in a finally block for clean resource cleanup.

### commands.py: Command Handlers (221 lines)

**Command Handlers**:

1. **cmd_add(app, args)** - Create a new habit
   - Validates name is non-empty string
   - Calls HabitService.add_habit()
   - Displays success with assigned ID

2. **cmd_list(app, args)** - Display all habits in a table
   - Retrieves all habits via HabitService
   - Formats table with ID, Name, Description (truncated), Created date
   - Shows message if no habits exist

3. **cmd_log(app, args)** - Log a habit completion
   - Parses habit_id as integer
   - Parses optional date (defaults to today)
   - Calls LoggingService.log_date()
   - Confirms completion with date

4. **cmd_streaks(app, args)** - Display weekly streak summaries
   - If habit_id provided: shows single habit streak with visual indicator
   - Otherwise: shows table of all streaks (Habit ID, Days Completed, Status)
   - Uses format_streak_display() for individual streaks

5. **cmd_export(app, args)** - Export habit data to CSV
   - Parses optional habit IDs as integers
   - Calls ExportService.export_to_csv()
   - Confirms file path on success

6. **cmd_help(app, args)** - Display usage information
   - Shows all available commands with examples
   - Guides users to proper command syntax

## Command Format

Each command follows a consistent error handling pattern:

```
try:
    # Service call
    # Formatting and output
except ValueError as e:
    # Input validation or not-found errors
    print error with sys.stderr
    sys.exit(1)
except Exception as e:
    # Unexpected errors
    print error with sys.stderr
    sys.exit(1)
```

## User Experience

### Success Output
- Habit created: `✓ Habit 'Morning Run' created successfully (ID: 1)`
- Habit logged: `✓ Logged completion for habit 1 on 2024-05-08`
- Export done: `✓ Data exported successfully to habits.csv`

### Error Output
- Invalid input: `✗ Error: Habit name must be a non-empty string`
- Not found: `✗ Error: Habit with ID 5 not found`
- File error: `✗ Error writing file: Permission denied`

### Commands Reference

```
add <name> [description]        Create a new habit
list                            Show all habits
log <habit_id> [date]           Log completion (date format: YYYY-MM-DD)
streaks [habit_id]              Show weekly streaks
export <path> [habit_ids...]    Export to CSV
help                            Show this help
```

## Error Handling Strategy

1. **Argument Parsing Errors**: Caught by argparse, show usage hint
2. **Input Validation**: ValueError from services, show user-friendly message
3. **Resource Errors**: IOError from file operations, show specific error
4. **Unexpected Errors**: Generic Exception handler with generic message

All errors exit with code 1 to signal failure to the shell.

## Dependencies

- `argparse`: Command-line argument parsing (built-in)
- `sys`: Exit codes and stderr output (built-in)
- `HabitTrackerApp`: Dependency injection for services
- `Formatters`: Output formatting utilities
- `Date utilities`: Date parsing and formatting
- `Service layer`: Business logic execution

## Testing Considerations

- Test each command with valid and invalid inputs
- Test date parsing with various formats
- Test table formatting with empty and populated data
- Test file export permissions and directory creation
- Test error messages for clarity and accuracy
- Test help command output completeness
