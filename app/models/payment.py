
class Payment:
    """Represents a payment made for an invoice."""

    def __init__(self, payment_id, invoice, amount):
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        self.payment_id = payment_id
        self.invoice = invoice
        self.amount = amount

    def is_fully_paid(self):
        """Check whether the payment covers the invoice total."""
        return self.amount >= self.invoice.total_amount

    def __str__(self):
        """Return a readable representation of the payment."""
        return f"Payment {self.payment_id} - {self.amount}"

