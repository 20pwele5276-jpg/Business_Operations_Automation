
from app.models.order import Order


class OrderService:
    """Handles business operations related to orders."""

    def create_order(self, order_id, customer, product, quantity):
        """Create and return a validated order."""
        return Order(order_id, customer, product, quantity)

    def get_order_total(self, order):
        """Return the total cost of an order."""
        return order.calculate_total()

    def get_order_info(self, order):
        """Return a readable description of an order."""
        return str(order)

