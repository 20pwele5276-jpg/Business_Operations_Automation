
import pytest

from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product
from app.models.report import Report


def create_sample_order():
    """Create a valid order that can be reused by multiple tests."""
    customer = Customer(1, "Ali", "ali@example.com")
    product = Product(1, "Laptop", 150000)

    return Order(
        1,
        customer,
        product,
        2,
    )


def test_product_creation():
    """Test that a valid product is created correctly."""
    product = Product(1, "Laptop", 150000)

    assert product.product_id == 1
    assert product.name == "Laptop"
    assert product.price == 150000


def test_product_rejects_negative_price():
    """Test that negative product prices are rejected."""
    with pytest.raises(ValueError):
        Product(1, "Laptop", -100)


def test_order_total():
    """Test that an order calculates its total correctly."""
    order = create_sample_order()

    assert order.calculate_total() == 300000


def test_order_rejects_invalid_quantity():
    """Test that zero or negative quantities are rejected."""
    customer = Customer(1, "Ali", "ali@example.com")
    product = Product(1, "Laptop", 150000)

    with pytest.raises(ValueError):
        Order(1, customer, product, 0)


def test_invoice_creation():
    """Test that an invoice gets the correct total from its order."""
    order = create_sample_order()
    invoice = Invoice(1, order)

    assert invoice.invoice_id == 1
    assert invoice.total_amount == 300000


def test_payment_status():
    """Test that a sufficient payment marks the invoice as fully paid."""
    order = create_sample_order()
    invoice = Invoice(1, order)
    payment = Payment(1, invoice, 300000)

    assert payment.is_fully_paid() is True


def test_payment_rejects_invalid_amount():
    """Test that zero or negative payments are rejected."""
    order = create_sample_order()
    invoice = Invoice(1, order)

    with pytest.raises(ValueError):
        Payment(1, invoice, 0)


def test_report_creation():
    """Test that a report stores and formats its information."""
    report = Report(
        1,
        "Sales Report",
        "Total sales: 300000",
    )

    assert report.report_id == 1
    assert report.title == "Sales Report"
    assert "Total sales: 300000" in report.generate()


def test_report_rejects_empty_title():
    """Test that an empty report title is rejected."""
    with pytest.raises(ValueError):
        Report(1, "", "Report content")