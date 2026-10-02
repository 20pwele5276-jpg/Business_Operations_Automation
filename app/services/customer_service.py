
from app.models.customer import Customer


class CustomerService:
    """Handles business operations related to customers."""

    def create_customer(self, customer_id, name, email):
        """Create and return a validated customer."""
        return Customer(customer_id, name, email)

    def get_customer_info(self, customer):
        """Return formatted information about a customer."""
        return customer.display_info()

