from app.database.database_manager import DatabaseManager
from app.exceptions.app_exceptions import DatabaseError
from app.utils.logger import AppLogger


class CustomerRepository:
    """Handles customer database operations."""

    def __init__(self, database_manager=None):
        self.database_manager = database_manager or DatabaseManager()
        self.logger = AppLogger()

    def save_customers(self, customers):
        """Save a list of customer records to the database."""
        saved_count = 0

        for customer in customers:
            try:
                customer_id = customer.get("customer_id")

                if customer_id is None:
                    customer_id = self._get_next_customer_id()

                name = customer.get("name", "").strip()
                email = customer.get("email", "").strip()

                if not name or not email:
                    raise DatabaseError(
                        "Customer name and email are required."
                    )

                self.database_manager.add_customer(
                    int(customer_id),
                    name,
                    email,
                )

                saved_count += 1

            except DatabaseError:
                raise

            except Exception as error:
                self.logger.error(
                    f"Failed to save customer: {error}"
                )
                raise DatabaseError(
                    f"Could not save customer: {error}"
                ) from error

        self.logger.info(
            f"Saved {saved_count} customer(s) to the database."
        )

        return saved_count

    def _get_next_customer_id(self):
        """Generate the next available customer ID."""
        customers = self.database_manager.get_customers()

        if not customers:
            return 1

        return max(customer[0] for customer in customers) + 1
