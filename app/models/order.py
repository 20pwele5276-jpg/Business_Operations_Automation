
class Order:
    """Represents a customer order in the business system."""

    def __init__(self, order_id, customer, product, quantity):
        if quantity <= 0:
            raise ValueError("Order quantity must be greater than zero.")

        self.order_id = order_id
        self.customer = customer
        self.product = product
        self.quantity = quantity

    def calculate_total(self):
        """Calculate the total cost of the order."""
        return self.product.price * self.quantity

    def __str__(self):
        """Return a readable representation of the order."""
        return f"Order {self.order_id}: {self.product.name} x {self.quantity}"

