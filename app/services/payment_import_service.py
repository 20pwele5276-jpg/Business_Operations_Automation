
from app.database.database_manager import DatabaseManager
from app.database.payment_repository import PaymentRepository
from app.utils.logger import AppLogger


class PaymentImportService:
    """Imports payment records into the database."""

    def __init__(self, payment_repository=None):
        if isinstance(payment_repository, DatabaseManager):
            payment_repository = PaymentRepository(payment_repository)
        self.payment_repository = payment_repository or PaymentRepository()
        self.logger = AppLogger()

    def import_payment(self, payment):
        """Save a payment record to the database."""
        payment_id = self.payment_repository.save_payment(payment)

        self.logger.info(
            f"Payment import completed: {payment_id}"
        )

        return payment_id

