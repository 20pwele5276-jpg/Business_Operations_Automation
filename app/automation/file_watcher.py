from pathlib import Path

from app.utils.logger import AppLogger


class FileWatcher:
    """Detects supported files in the input folder."""

    SUPPORTED_EXTENSIONS = {".csv", ".json", ".xlsx", ".xls"}

    def __init__(self, input_folder="data/input"):
        self.input_folder = Path(input_folder)
        self.input_folder.mkdir(parents=True, exist_ok=True)
        self.logger = AppLogger()

    def get_new_files(self):
        """Return supported files currently present in the input folder."""
        files = []

        for file_path in self.input_folder.iterdir():
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ):
                files.append(file_path)

        self.logger.info(
            f"File watcher found {len(files)} supported file(s)."
        )

        return files
