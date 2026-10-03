
import pytest

from app.exceptions.customer_exceptions import InvalidCustomerError
from app.models.customer import Customer


def test_create_customer():
    """Test that a valid customer is created correctly."""
    customer = Customer(1, "Ali", "ali@example.com")

    assert customer.customer_id == 1
    assert customer.name == "Ali"
    assert customer.email == "ali@example.com"


def test_customer_display_info():
    """Test the customer's formatted information."""
    customer = Customer(1, "Ali", "ali@example.com")

    assert customer.display_info() == (
        "Customer ID: 1, Name: Ali, Email: ali@example.com"
    )


def test_invalid_customer_name():
    """Test that an empty customer name raises an exception."""
    with pytest.raises(InvalidCustomerError):
        Customer(1, "", "ali@example.com")


def test_invalid_customer_email():
    """Test that an invalid email raises an exception."""
    with pytest.raises(InvalidCustomerError):
        Customer(1, "Ali", "invalid-email")
