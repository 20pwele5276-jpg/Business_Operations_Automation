
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


def test_multiple_workspaces_and_manual_business_records(tmp_path):
    """Test separate business workspaces and manual record creation."""
    from app.database.customer_repository import CustomerRepository
    from app.database.database_manager import DatabaseManager
    from app.database.invoice_repository import InvoiceRepository
    from app.database.order_repository import OrderRepository
    from app.database.payment_repository import PaymentRepository
    from app.database.product_repository import ProductRepository
    from app.database.workspace_manager import WorkspaceManager

    workspace_manager = WorkspaceManager(base_folder=tmp_path / "workspaces")

    first = workspace_manager.create_workspace("Alpha Shop", "Retail", "PKR")
    second = workspace_manager.create_workspace("Beta Shop", "Wholesale", "USD")

    assert len(workspace_manager.list_workspaces()) == 2
    assert {ws["business_name"] for ws in workspace_manager.list_workspaces()} == {"Alpha Shop", "Beta Shop"}

    for profile in (first, second):
        database = DatabaseManager(workspace_manager.get_database_path(profile["workspace_id"]))
        database.create_tables()

        customer_repo = CustomerRepository(database)
        product_repo = ProductRepository(database)
        order_repo = OrderRepository(database)
        invoice_repo = InvoiceRepository(database)
        payment_repo = PaymentRepository(database)

        saved_customers = customer_repo.save_customers([
            {"name": f"Customer {profile['workspace_id']}", "email": f"{profile['workspace_id']}@example.com"}
        ])
        saved_products = product_repo.save_products([
            {"name": f"Product {profile['workspace_id']}", "price": 250.0}
        ])

        assert saved_customers == 1
        assert saved_products == 1

        customer = database.get_customers()[0]
        product = database.get_products()[0]

        order_id = order_repo.save_order({
            "customer_id": customer[0],
            "product_id": product[0],
            "quantity": 2,
        })
        invoice_id = invoice_repo.save_invoice({
            "order_id": order_id,
            "total_amount": 500.0,
        })
        payment_id = payment_repo.save_payment({
            "invoice_id": invoice_id,
            "amount": 500.0,
        })

        assert database.get_orders() == [(order_id, customer[0], product[0], 2)]
        assert database.get_invoices() == [(invoice_id, order_id, 500.0)]
        assert database.get_payments() == [(payment_id, invoice_id, 500.0)]
