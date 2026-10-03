
from app.database.database_manager import DatabaseManager
from app.exceptions.app_exceptions import DatabaseError
from app.utils.logger import AppLogger


class ProductRepository:
    """Handles product database operations."""

    def __init__(self, database_manager=None):
        self.database_manager = database_manager or DatabaseManager()
        self.logger = AppLogger()

    def save_products(self, products):
        """Save products while avoiding duplicate product names."""
        saved_count = 0

        for product in products:
            try:
                name = str(product.get("name", "")).strip()
                price = product.get("price")

                if not name or price is None:
                    raise DatabaseError(
                        "Product name and price are required."
                    )

                price = float(price)

                if price < 0:
                    raise DatabaseError(
                        "Product price cannot be negative."
                    )

                existing_product = self._find_by_name(name)

                if existing_product:
                    self.logger.info(
                        f"Product already exists: {name}"
                    )
                    continue

                product_id = self._get_next_product_id()

                self.database_manager.add_product(
                    product_id,
                    name,
                    price,
                )

                saved_count += 1

            except DatabaseError:
                raise

            except Exception as error:
                self.logger.error(
                    f"Failed to save product: {error}"
                )
                raise DatabaseError(
                    f"Could not save product: {error}"
                ) from error

        self.logger.info(
            f"Saved {saved_count} new product(s) to the database."
        )

        return saved_count

    def _find_by_name(self, name):
        """Find an existing product using its name."""
        products = self.database_manager.get_products()

        for product in products:
            if product[1].lower() == name.lower():
                return product

        return None

    def _get_next_product_id(self):
        """Generate the next available product ID."""
        products = self.database_manager.get_products()

        if not products:
            return 1

        return max(product[0] for product in products) + 1
