
from app.database.database_manager import DatabaseManager
from app.exceptions.app_exceptions import DatabaseError
from app.utils.logger import AppLogger


class InvoiceRepository:
    """Handles invoice database operations."""

    def __init__(self, database_manager=None):
        self.database_manager = database_manager or DatabaseManager()
        self.logger = AppLogger()

    def save_invoice(self, invoice):
        """Save an invoice after validating the order reference."""
        try:
            order_id = invoice.get("order_id")
            total_amount = invoice.get("total_amount")

            if order_id is None:
                raise DatabaseError("Order ID is required.")

            if total_amount is None:
                raise DatabaseError("Invoice total amount is required.")

            total_amount = float(total_amount)

            if total_amount < 0:
                raise DatabaseError(
                    "Invoice total amount cannot be negative."
                )

            if not self._order_exists(order_id):
                raise DatabaseError(
                    f"Order does not exist: {order_id}"
                )

            invoice_id = self._get_next_invoice_id()

            self.database_manager.add_invoice(
                invoice_id,
                int(order_id),
                total_amount,
            )

            self.logger.info(
                f"Invoice saved successfully: {invoice_id}"
            )

            return invoice_id

        except DatabaseError:
            raise

        except Exception as error:
            self.logger.error(
                f"Failed to save invoice: {error}"
            )
            raise DatabaseError(
                f"Could not save invoice: {error}"
            ) from error

    def _order_exists(self, order_id):
        """Check whether an order exists."""
        orders = self.database_manager.get_orders()

        return any(
            order[0] == int(order_id)
            for order in orders
        )

    def _get_next_invoice_id(self):
        """Generate the next available invoice ID."""
        invoices = self.database_manager.get_invoices()

        if not invoices:
            return 1

        return max(invoice[0] for invoice in invoices) + 1
