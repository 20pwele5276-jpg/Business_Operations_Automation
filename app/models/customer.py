
from app.exceptions.customer_exceptions import InvalidCustomerError


class Customer:
    """Represents a customer in the business system."""

    def __init__(self, customer_id, name, email):
        if not name.strip():
            raise InvalidCustomerError("Customer name cannot be empty.")

        if "@" not in email:
            raise InvalidCustomerError("Customer email must contain '@'.")

        self.customer_id = customer_id
        self.name = name
        self.email = email

    def display_info(self):
        """Return basic customer information."""
        return f"Customer ID: {self.customer_id}, Name: {self.name}, Email: {self.email}"

    def __str__(self):
        """Return a readable representation of the customer."""
        return f"{self.name} ({self.email})"

