from pathlib import Path

from app.database.database_manager import DatabaseManager


class ReportGenerator:
    """Generates business reports from stored database records."""

    def __init__(self, database_manager=None):
        self.database_manager = database_manager or DatabaseManager()

    def generate_sales_summary(self):
        """Generate a summary of orders and sales."""
        orders = self.database_manager.get_orders()
        products = {
            product[0]: product
            for product in self.database_manager.get_products()
        }

        total_orders = len(orders)
        total_quantity = 0
        total_sales = 0.0

        for order in orders:
            order_id, customer_id, product_id, quantity = order
            product = products.get(product_id)

            if product:
                total_quantity += quantity
                total_sales += product[2] * quantity

        return {
            "total_orders": total_orders,
            "total_quantity": total_quantity,
            "total_sales": total_sales,
        }

    def generate_report_text(self):
        """Create a readable text version of the sales report."""
        summary = self.generate_sales_summary()

        return (
            "BUSINESS SALES REPORT\n"
            "=====================\n\n"
            f"Total Orders: {summary['total_orders']}\n"
            f"Total Items Sold: {summary['total_quantity']}\n"
            f"Total Sales: {summary['total_sales']:.2f}\n"
        )

    def save_report(self, file_path):
        """Generate and save the report to a text file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        report_text = self.generate_report_text()
        file_path.write_text(report_text, encoding="utf-8")
