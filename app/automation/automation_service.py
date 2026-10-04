
from pathlib import Path

from app.automation.backup_service import BackupService
from app.automation.file_watcher import FileWatcher
from app.database.customer_repository import CustomerRepository
from app.database.database_manager import DatabaseManager
from app.database.invoice_repository import InvoiceRepository
from app.database.order_repository import OrderRepository
from app.database.payment_repository import PaymentRepository
from app.database.product_repository import ProductRepository
from app.reports.report_generator import ReportGenerator
from app.reports.validation_report import ValidationReport
from app.services.customer_import_service import CustomerImportService
from app.services.file_processing_service import FileProcessingService
from app.services.invoice_import_service import InvoiceImportService
from app.services.order_import_service import OrderImportService
from app.services.payment_import_service import PaymentImportService
from app.services.product_import_service import ProductImportService
from app.utils.file_manager import FileManager
from app.utils.logger import AppLogger


class AutomationService:
    """Coordinates the automated business file processing workflow."""

    REQUIRED_FIELDS = {
        "customers": ["customer_id", "name", "email"],
        "products": ["product_id", "name", "price"],
        "orders": ["customer_id", "product_id", "quantity"],
        "invoices": ["order_id", "total_amount"],
        "payments": ["invoice_id", "amount"],
    }

    def __init__(
        self,
        input_folder="data/input",
        processed_folder="data/processed",
        archive_folder="data/archive",
        database_path="data/business.db",
        backup_folder="data/backup",
    ):
        self.input_folder = Path(input_folder)
        self.processed_folder = Path(processed_folder)
        self.archive_folder = Path(archive_folder)

        self.watcher = FileWatcher(self.input_folder)
        self.processor = FileProcessingService()

        self.database_manager = DatabaseManager(
            database_path
        )

        self.customer_import_service = CustomerImportService(
            CustomerRepository(self.database_manager)
        )
        self.product_import_service = ProductImportService(
            ProductRepository(self.database_manager)
        )
        self.order_import_service = OrderImportService(
            OrderRepository(self.database_manager)
        )
        self.invoice_import_service = InvoiceImportService(
            InvoiceRepository(self.database_manager)
        )
        self.payment_import_service = PaymentImportService(
            PaymentRepository(self.database_manager)
        )

        self.report_generator = ReportGenerator(
            self.database_manager
        )

        self.validation_report = ValidationReport()

        self.backup_service = BackupService(
            database_path=database_path,
            backup_folder=backup_folder,
        )

        self.file_manager = FileManager(
            self.input_folder
        )

        self.logger = AppLogger()

        self.processed_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.archive_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.database_manager.create_tables()

    def process_pending_files(self, required_fields=None):
        """Process supported files currently waiting in the input folder."""

        files = self.watcher.get_new_files()
        results = []

        for file_path in files:
            output_path = (
                self.processed_folder / file_path.name
            )

            archive_path = (
                self.archive_folder / file_path.name
            )

            try:
                file_required_fields = required_fields

                if file_required_fields is None:
                    file_required_fields = (
                        self._get_required_fields(
                            file_path
                        )
                    )

                result = self.processor.process_file(
                    file_path,
                    output_path,
                    file_required_fields,
                )

                # Generate a report when validation errors are found.
                if result["invalid_records"]:
                    validation_report_path = (
                        self.validation_report.save_report(
                            result["invalid_records"],
                            f"{file_path.stem}_validation_errors.csv",
                        )
                    )

                    result["validation_report"] = str(
                        validation_report_path
                    )

                    self.logger.warning(
                        f"Validation report generated: "
                        f"{validation_report_path}"
                    )

                self._import_processed_data(
                    file_path,
                    output_path,
                    result,
                )

                self.file_manager.move_file(
                    file_path.name,
                    self.archive_folder,
                )

                self.logger.info(
                    f"Original file archived: "
                    f"{archive_path.name}"
                )

                results.append(result)

            except Exception as error:
                self.logger.error(
                    f"Automation failed for "
                    f"{file_path.name}: {error}"
                )

        if results:
            # Keep the backup database synchronized with the
            # database manager currently used by the service.
            self.backup_service.database_path = (
                self.database_manager.database_path
            )

            # Create a database backup after successful processing.
            backup_path = (
                self.backup_service.backup_database()
            )

            self.logger.info(
                f"Automated database backup created: "
                f"{backup_path}"
            )

            report_path = Path(
                "reports/sales_report.txt"
            )

            self.report_generator.save_report(
                report_path
            )

            self.logger.info(
                f"Automated sales report generated: "
                f"{report_path}"
            )

            for result in results:
                result["backup_created"] = str(
                    backup_path
                )

                result["report_generated"] = str(
                    report_path
                )

        self.logger.info(
            "Automation workflow completed."
        )

        return results

    def _get_required_fields(self, file_path):
        """Return required fields based on the business file name."""

        file_type = file_path.stem.lower()

        return self.REQUIRED_FIELDS.get(
            file_type,
            [],
        )

    def _read_processed_data(self, output_path):
        """Read processed data from CSV, JSON, or Excel."""

        extension = output_path.suffix.lower()

        if extension == ".csv":
            return self.processor.csv_processor.read_file(
                output_path
            )

        if extension == ".json":
            return self.processor.json_processor.read_file(
                output_path
            )

        if extension in [".xlsx", ".xls"]:
            dataframe = (
                self.processor.excel_processor.read_file(
                    output_path
                )
            )

            return dataframe.to_dict(
                orient="records"
            )

        return []

    def _import_processed_data(
        self,
        file_path,
        output_path,
        result,
    ):
        """Import processed records into the appropriate database table."""

        file_type = file_path.stem.lower()

        rows = self._read_processed_data(
            output_path
        )

        if file_type == "customers":
            saved_count = (
                self.customer_import_service.import_customers(
                    rows
                )
            )

            result["customers_saved"] = saved_count

        elif file_type == "products":
            saved_count = (
                self.product_import_service.import_products(
                    rows
                )
            )

            result["products_saved"] = saved_count

        elif file_type == "orders":
            saved_count = 0

            for order in rows:
                self.order_import_service.import_order(
                    order
                )

                saved_count += 1

            result["orders_saved"] = saved_count

        elif file_type == "invoices":
            saved_count = 0

            for invoice in rows:
                self.invoice_import_service.import_invoice(
                    invoice
                )

                saved_count += 1

            result["invoices_saved"] = saved_count

        elif file_type == "payments":
            saved_count = 0

            for payment in rows:
                self.payment_import_service.import_payment(
                    payment
                )

                saved_count += 1

            result["payments_saved"] = saved_count
