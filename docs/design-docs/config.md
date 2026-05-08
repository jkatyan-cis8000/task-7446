# Configuration Layer Design

## Overview

The config layer provides centralized configuration management for the habit tracker application. It handles:
- Database path and directory management
- Application settings and thresholds
- Environment variable overrides
- Initialization of runtime directories

All configuration is loaded at module import time, making settings available throughout the application via simple imports.

## Design Philosophy

**Twelve-Factor App Principles**
- Environment variables for deployment-specific config
- Sensible defaults for development and testing
- No hardcoded paths or magic numbers
- Settings organized by concern

**Single Source of Truth**
- All configuration in one place (`settings.py`)
- Imported by multiple layers with confidence
- Changes propagate automatically
- Easy to audit and modify

## Configuration Items

### DB_PATH

Path to the SQLite database file.

**Definition:**
```python
DB_PATH = os.getenv("HABIT_TRACKER_DB", str(DB_DIR / "habits.db"))
```

**Default:** `~/.habit_tracker/habits.db`

**Environment Variable:** `HABIT_TRACKER_DB`

**Usage:**
- Read by `HabitDB.__init__()` to establish database connection
- Can be overridden for testing: `export HABIT_TRACKER_DB=/tmp/test.db`
- Directory is created automatically by `create_db_directory()`

**Example:**
```python
from src.config.settings import DB_PATH
db = HabitDB(DB_PATH)
```

### DB_DIR

Directory where the database file is stored.

**Definition:**
```python
DB_DIR = Path.home() / ".habit_tracker"
```

**Value:** `~/.habit_tracker`

**Usage:**
- Parent directory for `DB_PATH`
- Created by `create_db_directory()` if it doesn't exist
- Centralized location for all habit tracker data

### DEFAULT_STREAK_THRESHOLD

Minimum number of days to establish a streak.

**Definition:**
```python
DEFAULT_STREAK_THRESHOLD = int(os.getenv("HABIT_TRACKER_STREAK_THRESHOLD", "1"))
```

**Default:** `1`

**Environment Variable:** `HABIT_TRACKER_STREAK_THRESHOLD`

**Usage:**
- Used by `StreakService` to determine active streaks
- Configurable for different tracking requirements
- Example: Set to 3 for "need 3+ days to count as active"

### WEEK_START_DAY

Day of week that defines the start of a week.

**Definition:**
```python
WEEK_START_DAY = int(os.getenv("HABIT_TRACKER_WEEK_START_DAY", "0"))
```

**Default:** `0` (Monday)

**Environment Variable:** `HABIT_TRACKER_WEEK_START_DAY`

**Valid Values:**
- `0`: Monday
- `1`: Tuesday
- `2`: Wednesday
- `3`: Thursday
- `4`: Friday
- `5`: Saturday
- `6`: Sunday

**Usage:**
- Used by `DateUtils.get_week_start()` to calculate week boundaries
- Used by `StreakService` for weekly streak calculations
- Different regions may use different week starts

## Helper Functions

### create_db_directory()

Ensures the database directory exists.

**Signature:**
```python
def create_db_directory() -> None:
    """Ensure database directory exists."""
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
```

**Behavior:**
- Creates all parent directories if needed
- Idempotent: safe to call multiple times
- Uses `exist_ok=True` to avoid errors if already exists
- Called automatically by `HabitDB.get_connection()`

**Usage:**
```python
from src.config.settings import create_db_directory

# Ensure database directory exists before connecting
create_db_directory()
```

## Design Decisions

### 1. Environment Variables for Configuration

**Choice:** Use `os.getenv()` with defaults

**Rationale:**
- Supports different deployment environments
- Development: Default values work out of the box
- Testing: Override via environment for test isolation
- Production: Customize via environment variables
- No code changes needed for different configs

**Pattern:**
```python
SETTING = os.getenv("ENV_VAR_NAME", "default_value")
```

### 2. Type Conversion

**Approach:** Convert to proper types at import time

**Rationale:**
- `int()` conversion ensures type safety for numeric values
- `str()` conversion for paths ensures compatibility
- Catches configuration errors early (at import)
- Application code doesn't need to validate types

### 3. Home Directory for Database

**Choice:** `Path.home() / ".habit_tracker"`

**Rationale:**
- Standard location for user-local application data
- Works across different operating systems
- Respects user's home directory (not hardcoded)
- No permissions issues for typical users
- Easy to find and backup

### 4. Settings as Module-Level Variables

**Approach:** All settings are module-level constants

**Rationale:**
- Simple import and use: `from src.config.settings import DB_PATH`
- No instantiation or configuration objects needed
- Settings available immediately at import time
- Efficient: loaded once at module import
- Easy for testing: environment variables set before import

### 5. Separation of Concerns

**Database Configuration:**
- `DB_PATH`: Where to store data
- `DB_DIR`: Where database directory is

**Streak Configuration:**
- `DEFAULT_STREAK_THRESHOLD`: What counts as a streak

**Calendar Configuration:**
- `WEEK_START_DAY`: How weeks are defined

**Rationale:** Group related settings together, making the module easy to understand and extend.

## Import Guidelines

The config layer may import from:
- `os`: Environment variable access
- `pathlib`: Cross-platform path handling
- `src.config`: Other config settings (for cross-references)

Config must NOT import from:
- Types layer (types.py)
- Repo layer (would create circular dependencies)
- Service, runtime, UI layers

## Usage Patterns

### In Application Initialization

```python
from src.config.settings import DB_PATH, create_db_directory
from src.repo.database import HabitDB

# Ensure directory exists first
create_db_directory()

# Then create database connection
db = HabitDB()
db.init_db()
```

### In Services

```python
from src.config.settings import DEFAULT_STREAK_THRESHOLD

def calculate_active(days_completed: int) -> bool:
    return days_completed >= DEFAULT_STREAK_THRESHOLD
```

### In Providers

```python
from src.config.settings import WEEK_START_DAY
from datetime import date, timedelta

def get_week_start(d: date) -> date:
    """Get Monday of the week containing date d."""
    days_since_start = (d.weekday() - WEEK_START_DAY) % 7
    return d - timedelta(days=days_since_start)
```

## Testing Considerations

### Environment Variable Override

For testing with different configurations:

```python
# In test setup
import os
os.environ["HABIT_TRACKER_DB"] = "/tmp/test_habits.db"

# Then import module (forces re-evaluation)
import importlib
import src.config.settings
importlib.reload(src.config.settings)

# Now src.config.settings.DB_PATH uses test database
```

### Testing create_db_directory()

```python
import tempfile
from pathlib import Path
from src.config.settings import create_db_directory

def test_create_db_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Simulate configuration
        test_path = Path(tmpdir) / "subdir" / "test.db"
        
        # Create directory
        create_db_directory()  # Would use actual config
        
        # Verify directory exists
        assert test_path.parent.exists()
```

## Extension Points

If configuration needs to grow:

1. **Add new settings:** Simply add new module-level variables with env overrides
2. **Add validation:** Create validation functions that check loaded config
3. **Add profiles:** Support dev/test/prod profiles via environment
4. **Add file-based config:** Load from `.env` or YAML file in addition to env vars

The current design supports these extensions without breaking existing code.

## Environment Variable Reference

| Variable | Default | Type | Purpose |
|----------|---------|------|---------|
| `HABIT_TRACKER_DB` | `~/.habit_tracker/habits.db` | string | Path to database file |
| `HABIT_TRACKER_STREAK_THRESHOLD` | `1` | int | Days needed for streak |
| `HABIT_TRACKER_WEEK_START_DAY` | `0` | int | Week start day (0=Mon) |

## Dependencies

- **os** (built-in): Environment variable access
- **pathlib** (built-in): Cross-platform path handling
