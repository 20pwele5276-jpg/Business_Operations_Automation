from pathlib import Path
import shutil

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

    def list_files(self):
        """Return a list of files in the folder."""
        return [file for file in self.folder_path.iterdir() if file.is_file()]

    def move_file(self, file_name, destination_folder):
        """Move a file from the current folder to another folder."""
        source_path = self.folder_path / file_name
        destination_path = Path(destination_folder)
        destination_path.mkdir(parents=True, exist_ok=True)

        shutil.move(str(source_path), str(destination_path / file_name))

