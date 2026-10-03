
from app.database.order_repository import OrderRepository
from app.utils.logger import AppLogger


class OrderImportService:
    """Imports order records into the database."""

    def __init__(self, order_repository=None):
        self.order_repository = order_repository or OrderRepository()
        self.logger = AppLogger()

    def import_order(self, order):
        """Save an order record to the database."""
        order_id = self.order_repository.save_order(order)

        self.logger.info(
            f"Order import completed: {order_id}"
        )

        return order_id