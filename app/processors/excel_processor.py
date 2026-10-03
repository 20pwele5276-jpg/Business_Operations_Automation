
import pandas as pd
from pathlib import Path


class ExcelProcessor:
    """Handles reading and writing Excel files."""

    def read_file(self, file_path):
        """Read an Excel file and return its data as a DataFrame."""
        file_path = Path(file_path)
        return pd.read_excel(file_path)

    def write_file(self, file_path, data):
        """Write a DataFrame to an Excel file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data.to_excel(file_path, index=False)
