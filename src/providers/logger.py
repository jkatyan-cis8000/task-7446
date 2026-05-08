"""Logging utilities for the habit tracker application."""

import logging
import sys
from typing import Optional


# Module-level logger instance
_logger: Optional[logging.Logger] = None


def setup_logger(name: str = "habit_tracker") -> logging.Logger:
    """
    Initialize and configure a logger for the application.

    Args:
        name: Name of the logger (default: "habit_tracker")

    Returns:
        Configured Logger instance
    """
    global _logger

    logger = logging.getLogger(name)

    # Only configure once
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    _logger = logger
    return logger


def get_logger(name: str = "habit_tracker") -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Name of the logger

    Returns:
        Logger instance
    """
    global _logger
    if _logger is None:
        _logger = setup_logger(name)
    return _logger


def log_info(msg: str) -> None:
    """
    Log an info-level message.

    Args:
        msg: Message to log
    """
    logger = get_logger()
    logger.info(msg)


def log_error(msg: str) -> None:
    """
    Log an error-level message.

    Args:
        msg: Message to log
    """
    logger = get_logger()
    logger.error(msg)


def log_debug(msg: str) -> None:
    """
    Log a debug-level message.

    Args:
        msg: Message to log
    """
    logger = get_logger()
    logger.debug(msg)
