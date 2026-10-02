
from app.models.payment import Payment


class PaymentService:
    """Handles business operations related to payments."""

    def create_payment(self, payment_id, invoice, amount):
        """Create and return a validated payment."""
        return Payment(payment_id, invoice, amount)

    def check_payment_status(self, payment):
        """Return whether the invoice has been fully paid."""
        return payment.is_fully_paid()

