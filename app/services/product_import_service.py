
from app.database.database_manager import DatabaseManager
from app.database.product_repository import ProductRepository
from app.utils.logger import AppLogger


class ProductImportService:
    """Imports cleaned product records into the database."""

    def __init__(self, product_repository=None):
        if isinstance(product_repository, DatabaseManager):
            product_repository = ProductRepository(product_repository)
        self.product_repository = product_repository or ProductRepository()
        self.logger = AppLogger()

    def import_products(self, products):
        """Save cleaned product records to the database."""
        saved_count = self.product_repository.save_products(products)

        self.logger.info(
            f"Product import completed: {saved_count} product(s) saved."
        )

        return saved_count
