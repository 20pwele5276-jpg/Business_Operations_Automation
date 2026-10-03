
import json
from pathlib import Path


class JSONProcessor:
    """Handles reading, writing, and validating JSON files."""

    def read_file(self, file_path):
        """Read a JSON file and return its data."""
        file_path = Path(file_path)

        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def write_file(self, file_path, data):
        """Write data to a JSON file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def validate_file(self, file_path):
        """Check whether a JSON file contains valid JSON."""
        try:
            self.read_file(file_path)
            return True
        except json.JSONDecodeError:
            return False

