
from app.database.database_manager import DatabaseManager
from app.exceptions.app_exceptions import DatabaseError
from app.utils.logger import AppLogger


class PaymentRepository:
    """Handles payment database operations."""

    def __init__(self, database_manager=None):
        self.database_manager = database_manager or DatabaseManager()
        self.logger = AppLogger()

    def save_payment(self, payment):
        """Save a payment after validating the invoice reference."""
        try:
            invoice_id = payment.get("invoice_id")
            amount = payment.get("amount")

            if invoice_id is None:
                raise DatabaseError("Invoice ID is required.")

            if amount is None:
                raise DatabaseError("Payment amount is required.")

            amount = float(amount)

            if amount <= 0:
                raise DatabaseError(
                    "Payment amount must be greater than zero."
                )

            if not self._invoice_exists(invoice_id):
                raise DatabaseError(
                    f"Invoice does not exist: {invoice_id}"
                )

            payment_id = self._get_next_payment_id()

            self.database_manager.add_payment(
                payment_id,
                int(invoice_id),
                amount,
            )

            self.logger.info(
                f"Payment saved successfully: {payment_id}"
            )

            return payment_id

        except DatabaseError:
            raise

        except Exception as error:
            self.logger.error(
                f"Failed to save payment: {error}"
            )
            raise DatabaseError(
                f"Could not save payment: {error}"
            ) from error

    def _invoice_exists(self, invoice_id):
        """Check whether an invoice exists."""
        invoices = self.database_manager.get_invoices()

        return any(
            invoice[0] == int(invoice_id)
            for invoice in invoices
        )

    def _get_next_payment_id(self):
        """Generate the next available payment ID."""
        payments = self.database_manager.get_payments()

        if not payments:
            return 1

        return max(payment[0] for payment in payments) + 1
