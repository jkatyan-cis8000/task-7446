"""
Main entry point for the habit tracker application.

This module provides the primary entry point for running the habit tracker CLI.
It handles application initialization, error handling, and cleanup.
"""

import sys

from src.ui.cli import main as cli_main


def main() -> None:
    """
    Main entry point for the habit tracker application.

    Initializes the CLI and passes command-line arguments to the CLI main function.
    Handles any uncaught exceptions and ensures proper cleanup.
    """
    try:
        cli_main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nApplication interrupted by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for keyboard interrupt
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
