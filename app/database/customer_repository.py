
from app.database.database_manager import DatabaseManager
from app.exceptions.app_exceptions import DatabaseError
from app.utils.logger import AppLogger


class CustomerRepository:
    """Handles customer database operations."""

    def __init__(self, database_manager=None):
        self.database_manager = database_manager or DatabaseManager()
        self.logger = AppLogger()

    def save_customers(self, customers):
        """Save customers while avoiding duplicate email addresses."""
        saved_count = 0

        for customer in customers:
            try:
                name = str(customer.get("name", "")).strip()
                email = str(customer.get("email", "")).strip()

                if not name or not email:
                    raise DatabaseError(
                        "Customer name and email are required."
                    )

                existing_customer = self._find_by_email(email)

                if existing_customer:
                    self.logger.info(
                        f"Customer already exists: {email}"
                    )
                    continue

                customer_id = self._get_next_customer_id()

                self.database_manager.add_customer(
                    customer_id,
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
            f"Saved {saved_count} new customer(s) to the database."
        )

        return saved_count

    def _find_by_email(self, email):
        """Find an existing customer using their email."""
        customers = self.database_manager.get_customers()

        for customer in customers:
            if customer[2].lower() == email.lower():
                return customer

        return None

    def _get_next_customer_id(self):
        """Generate the next available customer ID."""
        customers = self.database_manager.get_customers()

        if not customers:
            return 1

        return max(customer[0] for customer in customers) + 1
