
class Product:
    """Represents a product in the business system."""

    def __init__(self, product_id, name, price):
        if not name.strip():
            raise ValueError("Product name cannot be empty.")

        if price < 0:
            raise ValueError("Product price cannot be negative.")

        self.product_id = product_id
        self.name = name
        self.price = price

    def display_info(self):
        """Return basic product information."""
        return f"Product ID: {self.product_id}, Name: {self.name}, Price: {self.price}"

    def __str__(self):
        """Return a readable representation of the product."""
        return f"{self.name} - {self.price}"

