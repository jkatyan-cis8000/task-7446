"""CSV file writing utilities for the habit tracker application."""

import csv
from pathlib import Path
from typing import List


def write_csv(
    filepath: str, headers: List[str], rows: List[List[str]]
) -> None:
    """
    Write data to a CSV file.

    Creates parent directories if they don't exist.

    Args:
        filepath: Path where the CSV file should be written
        headers: List of column headers
        rows: List of rows, where each row is a list of strings

    Raises:
        IOError: If the file cannot be written
        ValueError: If headers or rows are invalid
    """
    if not headers:
        raise ValueError("Headers list cannot be empty")

    if not isinstance(headers, list) or not all(isinstance(h, str) for h in headers):
        raise ValueError("All headers must be strings")

    if not isinstance(rows, list):
        raise ValueError("Rows must be a list")

    for row in rows:
        if not isinstance(row, list):
            raise ValueError("Each row must be a list")
        if len(row) != len(headers):
            raise ValueError(
                f"Row length {len(row)} does not match headers length {len(headers)}"
            )
        if not all(isinstance(cell, str) for cell in row):
            raise ValueError("All cells must be strings")

    # Ensure output directory exists
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to CSV file
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
    except IOError as e:
        raise IOError(f"Failed to write CSV file: {filepath}") from e
