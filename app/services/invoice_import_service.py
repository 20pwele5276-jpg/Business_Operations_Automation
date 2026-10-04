
from app.database.database_manager import DatabaseManager
from app.database.invoice_repository import InvoiceRepository
from app.utils.logger import AppLogger


class InvoiceImportService:
    """Imports invoice records into the database."""

    def __init__(self, invoice_repository=None):
        if isinstance(invoice_repository, DatabaseManager):
            invoice_repository = InvoiceRepository(invoice_repository)
        self.invoice_repository = invoice_repository or InvoiceRepository()
        self.logger = AppLogger()

    def import_invoice(self, invoice):
        """Save an invoice record to the database."""
        invoice_id = self.invoice_repository.save_invoice(invoice)

        self.logger.info(
            f"Invoice import completed: {invoice_id}"
        )

        return invoice_id
