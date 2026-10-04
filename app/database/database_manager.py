
import sqlite3
from pathlib import Path


class DatabaseManager:
    """Manages the SQLite database for a business workspace."""

    def __init__(self, database_path="data/business.db"):
        self.database_path = Path(database_path)

        # Create the database folder if it does not exist.
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def connect(self):
        """Create a database connection with foreign-key support."""

        connection = sqlite3.connect(
            self.database_path
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def create_tables(self):
        """Create all main business tables."""

        with self.connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (customer_id)
                        REFERENCES customers(customer_id),
                    FOREIGN KEY (product_id)
                        REFERENCES products(product_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id INTEGER PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    total_amount REAL NOT NULL,
                    FOREIGN KEY (order_id)
                        REFERENCES orders(order_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY,
                    invoice_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (invoice_id)
                        REFERENCES invoices(invoice_id)
                )
            """)

    def add_customer(self, customer_id, name, email):
        """Store a customer in the database."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO customers
                (customer_id, name, email)
                VALUES (?, ?, ?)
                """,
                (
                    customer_id,
                    name,
                    email,
                ),
            )

    def add_product(self, product_id, name, price):
        """Store a product in the database."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO products
                (product_id, name, price)
                VALUES (?, ?, ?)
                """,
                (
                    product_id,
                    name,
                    price,
                ),
            )

    def add_order(
        self,
        order_id,
        customer_id,
        product_id,
        quantity,
    ):
        """Store an order in the database."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO orders
                (order_id, customer_id, product_id, quantity)
                VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    customer_id,
                    product_id,
                    quantity,
                ),
            )

    def add_invoice(
        self,
        invoice_id,
        order_id,
        total_amount,
    ):
        """Store an invoice in the database."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO invoices
                (invoice_id, order_id, total_amount)
                VALUES (?, ?, ?)
                """,
                (
                    invoice_id,
                    order_id,
                    total_amount,
                ),
            )

    def add_payment(
        self,
        payment_id,
        invoice_id,
        amount,
    ):
        """Store a payment in the database."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO payments
                (payment_id, invoice_id, amount)
                VALUES (?, ?, ?)
                """,
                (
                    payment_id,
                    invoice_id,
                    amount,
                ),
            )

    def get_customers(self):
        """Return all customers."""

        with self.connect() as connection:
            return connection.execute(
                """
                SELECT customer_id, name, email
                FROM customers
                """
            ).fetchall()

    def get_products(self):
        """Return all products."""

        with self.connect() as connection:
            return connection.execute(
                """
                SELECT product_id, name, price
                FROM products
                """
            ).fetchall()

    def get_orders(self):
        """Return all orders."""

        with self.connect() as connection:
            return connection.execute(
                """
                SELECT order_id, customer_id,
                       product_id, quantity
                FROM orders
                """
            ).fetchall()

    def get_invoices(self):
        """Return all invoices."""

        with self.connect() as connection:
            return connection.execute(
                """
                SELECT invoice_id, order_id, total_amount
                FROM invoices
                """
            ).fetchall()

    def get_payments(self):
        """Return all payments."""

        with self.connect() as connection:
            return connection.execute(
                """
                SELECT payment_id, invoice_id, amount
                FROM payments
                """
            ).fetchall()
