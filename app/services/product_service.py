
from app.models.product import Product


class ProductService:
    """Handles business operations related to products."""

    def create_product(self, product_id, name, price):
        """Create and return a validated product."""
        return Product(product_id, name, price)

    def get_product_info(self, product):
        """Return formatted information about a product."""
        return product.display_info()

