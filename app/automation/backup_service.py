
from datetime import datetime
from pathlib import Path
import shutil

from app.exceptions.app_exceptions import FileProcessingError
from app.utils.logger import AppLogger


class BackupService:
    """Creates backups of important application files."""

    def __init__(
        self,
        database_path="data/business.db",
        backup_folder="data/backup",
    ):
        self.database_path = Path(database_path)
        self.backup_folder = Path(backup_folder)
        self.logger = AppLogger()

        self.backup_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

    def backup_database(self):
        """Create a timestamped backup of the SQLite database."""

        try:
            if not self.database_path.is_file():
                raise FileProcessingError(
                    f"Database file does not exist: {self.database_path}"
                )

            # Make sure the backup folder exists even if the
            # current working directory has changed.
            self.backup_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            backup_file = (
                self.backup_folder
                / f"business_backup_{timestamp}.db"
            )

            shutil.copy2(
                self.database_path,
                backup_file,
            )

            self.logger.info(
                f"Database backup created: "
                f"{backup_file.name}"
            )

            return backup_file

        except FileProcessingError:
            raise

        except Exception as error:
            self.logger.error(
                f"Database backup failed: {error}"
            )

            raise FileProcessingError(
                "Could not create database backup."
            ) from error
