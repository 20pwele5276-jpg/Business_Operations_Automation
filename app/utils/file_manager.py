
from pathlib import Path


class FileManager:
    """Handles basic file and folder operations for the application."""

    def __init__(self, folder_path):
        # Store the folder path as a Path object for easier file handling.
        self.folder_path = Path(folder_path)

    def create_folder(self):
        """Create the folder if it does not already exist."""
        self.folder_path.mkdir(parents=True, exist_ok=True)

    def write_file(self, file_name, content):
        """Create a file and write text content into it."""
        file_path = self.folder_path / file_name
        file_path.write_text(content, encoding="utf-8")

    def read_file(self, file_name):
        """Read and return the text content of a file."""
        file_path = self.folder_path / file_name
        return file_path.read_text(encoding="utf-8")

    def file_exists(self, file_name):
        """Check whether a specific file exists in the folder."""
        file_path = self.folder_path / file_name
        return file_path.is_file()

