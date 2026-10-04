
from app.database.customer_repository import CustomerRepository
from app.database.database_manager import DatabaseManager
from app.utils.logger import AppLogger


class CustomerImportService:
    """Imports cleaned customer records into the database."""

    def __init__(self, customer_repository=None):
        if isinstance(customer_repository, DatabaseManager):
            customer_repository = CustomerRepository(customer_repository)
        self.customer_repository = customer_repository or CustomerRepository()
        self.logger = AppLogger()

    def import_customers(self, customers):
        """Save cleaned customer records to the database."""
        saved_count = self.customer_repository.save_customers(customers)

        self.logger.info(
            f"Customer import completed: {saved_count} customer(s) saved."
        )

        return saved_count
