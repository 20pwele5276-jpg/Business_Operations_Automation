
from pathlib import Path

from app.automation.file_watcher import FileWatcher
from app.database.database_manager import DatabaseManager
from app.reports.report_generator import ReportGenerator
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
    ):
        self.input_folder = Path(input_folder)
        self.processed_folder = Path(processed_folder)
        self.archive_folder = Path(archive_folder)

        self.watcher = FileWatcher(self.input_folder)
        self.processor = FileProcessingService()

        self.customer_import_service = CustomerImportService()
        self.product_import_service = ProductImportService()
        self.order_import_service = OrderImportService()
        self.invoice_import_service = InvoiceImportService()
        self.payment_import_service = PaymentImportService()

        self.database_manager = DatabaseManager()
        self.report_generator = ReportGenerator(self.database_manager)

        self.file_manager = FileManager(self.input_folder)
        self.logger = AppLogger()

        self.processed_folder.mkdir(parents=True, exist_ok=True)
        self.archive_folder.mkdir(parents=True, exist_ok=True)

        self.database_manager.create_tables()

    def process_pending_files(self, required_fields=None):
        """Process supported files currently waiting in the input folder."""
        files = self.watcher.get_new_files()
        results = []

        for file_path in files:
            output_path = self.processed_folder / file_path.name
            archive_path = self.archive_folder / file_path.name

            try:
                file_required_fields = required_fields

                if file_required_fields is None:
                    file_required_fields = self._get_required_fields(
                        file_path
                    )

                result = self.processor.process_file(
                    file_path,
                    output_path,
                    file_required_fields,
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
                    f"Original file archived: {archive_path.name}"
                )

                results.append(result)

            except Exception as error:
                self.logger.error(
                    f"Automation failed for {file_path.name}: {error}"
                )

        if results:
            report_path = Path("reports/sales_report.txt")

            self.report_generator.save_report(report_path)

            self.logger.info(
                f"Automated sales report generated: {report_path}"
            )

            for result in results:
                result["report_generated"] = str(report_path)

        self.logger.info("Automation workflow completed.")

        return results

    def _get_required_fields(self, file_path):
        """Return required fields based on the business file name."""
        file_type = file_path.stem.lower()

        return self.REQUIRED_FIELDS.get(
            file_type,
            [],
        )

    def _import_processed_data(self, file_path, output_path, result):
        """Import processed records into the appropriate database table."""
        file_type = file_path.stem.lower()

        if file_type == "customers":
            customers = self.processor.csv_processor.read_file(
                output_path
            )

            saved_count = (
                self.customer_import_service.import_customers(
                    customers
                )
            )

            result["customers_saved"] = saved_count

        elif file_type == "products":
            products = self.processor.csv_processor.read_file(
                output_path
            )

            saved_count = (
                self.product_import_service.import_products(
                    products
                )
            )

            result["products_saved"] = saved_count

        elif file_type == "orders":
            orders = self.processor.csv_processor.read_file(
                output_path
            )

            saved_count = 0

            for order in orders:
                self.order_import_service.import_order(order)
                saved_count += 1

            result["orders_saved"] = saved_count

        elif file_type == "invoices":
            invoices = self.processor.csv_processor.read_file(
                output_path
            )

            saved_count = 0

            for invoice in invoices:
                self.invoice_import_service.import_invoice(invoice)
                saved_count += 1

            result["invoices_saved"] = saved_count

        elif file_type == "payments":
            payments = self.processor.csv_processor.read_file(
                output_path
            )

            saved_count = 0

            for payment in payments:
                self.payment_import_service.import_payment(payment)
                saved_count += 1

            result["payments_saved"] = saved_count

    def _is_customer_file(self, file_path):
        """Check whether a file contains customer records."""
        return (
            file_path.stem.lower() == "customers"
            and file_path.suffix.lower() == ".csv"
        )

    def _is_product_file(self, file_path):
        """Check whether a file contains product records."""
        return (
            file_path.stem.lower() == "products"
            and file_path.suffix.lower() == ".csv"
        )

    def _is_order_file(self, file_path):
        """Check whether a file contains order records."""
        return (
            file_path.stem.lower() == "orders"
            and file_path.suffix.lower() == ".csv"
        )

    def _is_invoice_file(self, file_path):
        """Check whether a file contains invoice records."""
        return (
            file_path.stem.lower() == "invoices"
            and file_path.suffix.lower() == ".csv"
        )

    def _is_payment_file(self, file_path):
        """Check whether a file contains payment records."""
        return (
            file_path.stem.lower() == "payments"
            and file_path.suffix.lower() == ".csv"
        )
