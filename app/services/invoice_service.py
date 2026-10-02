
from app.models.invoice import Invoice


class InvoiceService:
    """Handles business operations related to invoices."""

    def create_invoice(self, invoice_id, order):
        """Create and return an invoice for an order."""
        return Invoice(invoice_id, order)

    def get_invoice_summary(self, invoice):
        """Return the formatted invoice summary."""
        return invoice.generate_summary()

