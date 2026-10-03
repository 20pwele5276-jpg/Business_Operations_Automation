
from app.database.database_manager import DatabaseManager
from app.exceptions.app_exceptions import DatabaseError
from app.utils.logger import AppLogger


class OrderRepository:
    """Handles order database operations."""

    def __init__(self, database_manager=None):
        self.database_manager = database_manager or DatabaseManager()
        self.logger = AppLogger()

    def save_order(self, order):
        """Save an order after validating customer and product references."""
        try:
            customer_id = order.get("customer_id")
            product_id = order.get("product_id")
            quantity = order.get("quantity")

            if customer_id is None:
                raise DatabaseError("Customer ID is required.")

            if product_id is None:
                raise DatabaseError("Product ID is required.")

            if quantity is None:
                raise DatabaseError("Order quantity is required.")

            quantity = int(quantity)

            if quantity <= 0:
                raise DatabaseError(
                    "Order quantity must be greater than zero."
                )

            if not self._customer_exists(customer_id):
                raise DatabaseError(
                    f"Customer does not exist: {customer_id}"
                )

            if not self._product_exists(product_id):
                raise DatabaseError(
                    f"Product does not exist: {product_id}"
                )

            order_id = self._get_next_order_id()

            self.database_manager.add_order(
                order_id,
                int(customer_id),
                int(product_id),
                quantity,
            )

            self.logger.info(
                f"Order saved successfully: {order_id}"
            )

            return order_id

        except DatabaseError:
            raise

        except Exception as error:
            self.logger.error(
                f"Failed to save order: {error}"
            )
            raise DatabaseError(
                f"Could not save order: {error}"
            ) from error

    def _customer_exists(self, customer_id):
        """Check whether a customer exists."""
        customers = self.database_manager.get_customers()

        return any(
            customer[0] == int(customer_id)
            for customer in customers
        )

    def _product_exists(self, product_id):
        """Check whether a product exists."""
        products = self.database_manager.get_products()

        return any(
            product[0] == int(product_id)
            for product in products
        )

    def _get_next_order_id(self):
        """Generate the next available order ID."""
        orders = self.database_manager.get_orders()

        if not orders:
            return 1

        return max(order[0] for order in orders) + 1
