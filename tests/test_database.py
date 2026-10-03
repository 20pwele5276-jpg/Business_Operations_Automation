
def test_database_creates_tables(tmp_path):
    """Test that all required database tables are created."""
    from app.database.database_manager import DatabaseManager

    database_path = tmp_path / "test.db"
    database = DatabaseManager(database_path)

    database.create_tables()

    with database.connect() as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

    table_names = {table[0] for table in tables}

    assert "customers" in table_names
    assert "products" in table_names
    assert "orders" in table_names
    assert "invoices" in table_names
    assert "payments" in table_names


def test_database_customer_and_product(tmp_path):
    """Test storing and retrieving customers and products."""
    from app.database.database_manager import DatabaseManager

    database_path = tmp_path / "test.db"
    database = DatabaseManager(database_path)

    database.create_tables()

    database.add_customer(
        1,
        "Ali",
        "ali@example.com",
    )

    database.add_product(
        1,
        "Laptop",
        150000,
    )

    assert database.get_customers() == [
        (1, "Ali", "ali@example.com")
    ]

    assert database.get_products() == [
        (1, "Laptop", 150000.0)
    ]


def test_database_order_invoice_payment(tmp_path):
    """Test storing related order, invoice, and payment records."""
    from app.database.database_manager import DatabaseManager

    database_path = tmp_path / "test.db"
    database = DatabaseManager(database_path)

    database.create_tables()

    database.add_customer(
        1,
        "Ali",
        "ali@example.com",
    )

    database.add_product(
        1,
        "Laptop",
        150000,
    )

    database.add_order(
        1,
        1,
        1,
        2,
    )

    database.add_invoice(
        1,
        1,
        300000,
    )

    database.add_payment(
        1,
        1,
        300000,
    )

    assert database.get_orders() == [
        (1, 1, 1, 2)
    ]

    assert database.get_invoices() == [
        (1, 1, 300000.0)
    ]

    assert database.get_payments() == [
        (1, 1, 300000.0)
    ]


def test_database_foreign_key_protection(tmp_path):
    """Test that invalid related records are rejected."""
    import sqlite3

    from app.database.database_manager import DatabaseManager

    database_path = tmp_path / "test.db"
    database = DatabaseManager(database_path)

    database.create_tables()

    try:
        database.add_order(
            1,
            999,
            999,
            2,
        )
        assert False, "Invalid foreign key was accepted."

    except sqlite3.IntegrityError:
        assert True
