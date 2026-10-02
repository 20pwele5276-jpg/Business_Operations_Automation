
class Invoice:
    """Represents an invoice generated for an order."""

    def __init__(self, invoice_id, order):
        self.invoice_id = invoice_id
        self.order = order
        self.total_amount = order.calculate_total()

    def generate_summary(self):
        """Return a basic invoice summary."""
        return (
            f"Invoice ID: {self.invoice_id}\n"
            f"Order ID: {self.order.order_id}\n"
            f"Customer: {self.order.customer.name}\n"
            f"Product: {self.order.product.name}\n"
            f"Quantity: {self.order.quantity}\n"
            f"Total Amount: {self.total_amount}"
        )

    def __str__(self):
        """Return a readable representation of the invoice."""
        return f"Invoice {self.invoice_id} - {self.total_amount}"

