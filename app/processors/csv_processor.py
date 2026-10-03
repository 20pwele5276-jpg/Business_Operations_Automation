
import csv
from pathlib import Path


class CSVProcessor:
    """Handles reading, writing, and validating CSV files."""

    def read_file(self, file_path):
        """Read a CSV file and return its rows as dictionaries."""
        file_path = Path(file_path)

        with file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)

    def write_file(self, file_path, rows, fieldnames):
        """Write rows of data to a CSV file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def validate_columns(self, file_path, required_columns):
        """Check whether a CSV file contains all required columns."""
        file_path = Path(file_path)

        with file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            actual_columns = reader.fieldnames or []

        missing_columns = [
            column for column in required_columns
            if column not in actual_columns
        ]

        return missing_columns

