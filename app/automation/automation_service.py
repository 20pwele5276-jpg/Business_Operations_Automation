
from pathlib import Path

from app.automation.file_watcher import FileWatcher
from app.services.customer_import_service import CustomerImportService
from app.services.file_processing_service import FileProcessingService
from app.utils.file_manager import FileManager
from app.utils.logger import AppLogger


class AutomationService:
    """Coordinates the automated business file processing workflow."""

    def __init__(
        self,
        input_folder="data/input",
        processed_folder="data/processed",
        archive_folder="data/archive",
    ):
        self.input_folder = Path(input_folder)
        self.processed_folder = Path(processed_folder)
        self.archive_folder = Path(archive_folder)

        self.watcher = FileWatcher(self.input_folder)
        self.processor = FileProcessingService()
        self.customer_import_service = CustomerImportService()
        self.file_manager = FileManager(self.input_folder)
        self.logger = AppLogger()

        self.processed_folder.mkdir(parents=True, exist_ok=True)
        self.archive_folder.mkdir(parents=True, exist_ok=True)

    def process_pending_files(self, required_fields):
        """Process supported files currently waiting in the input folder."""
        files = self.watcher.get_new_files()
        results = []

        for file_path in files:
            output_path = self.processed_folder / file_path.name
            archive_path = self.archive_folder / file_path.name

            try:
                result = self.processor.process_file(
                    file_path,
                    output_path,
                    required_fields,
                )

                if self._is_customer_file(file_path):
                    customers = self.processor.csv_processor.read_file(
                        output_path
                    )

                    saved_count = (
                        self.customer_import_service.import_customers(
                            customers
                        )
                    )

                    result["customers_saved"] = saved_count

                self.file_manager.move_file(
                    file_path.name,
                    self.archive_folder,
                )

                self.logger.info(
                    f"Original file archived: {archive_path.name}"
                )

                self.logger.info(
                    f"Automation completed for: {file_path.name}"
                )

                results.append(result)

            except Exception as error:
                self.logger.error(
                    f"Automation failed for {file_path.name}: {error}"
                )

        return results

    def _is_customer_file(self, file_path):
        """Check whether a file contains customer records."""
        return (
            file_path.stem.lower() == "customers"
            and file_path.suffix.lower() == ".csv"
        )
