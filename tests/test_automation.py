
from pathlib import Path

from app.automation.automation_service import AutomationService
from app.database.database_manager import DatabaseManager
from app.database.customer_repository import CustomerRepository
from app.services.customer_import_service import CustomerImportService


def create_test_service(tmp_path):
    """Create an automation service using a temporary test database."""
    input_folder = tmp_path / "input"
    processed_folder = tmp_path / "processed"
    archive_folder = tmp_path / "archive"
    database_path = tmp_path / "business.db"

    input_folder.mkdir()

    service = AutomationService(
        input_folder=input_folder,
        processed_folder=processed_folder,
        archive_folder=archive_folder,
    )

    database = DatabaseManager(database_path)
    database.create_tables()

    customer_repository = CustomerRepository(database)

    service.database_manager = database
    service.customer_import_service = CustomerImportService(
        customer_repository
    )
    service.report_generator.database_manager = database

    return service


def test_automation_processes_customer_file(tmp_path):
    """Test that a customer file is processed and saved to the database."""
    service = create_test_service(tmp_path)

    customer_file = service.input_folder / "customers.csv"

    customer_file.write_text(
        "customer_id,name,email\n"
        "1,Ali,ali@example.com\n"
        "2,Sara,sara@example.com\n",
        encoding="utf-8",
    )

    results = service.process_pending_files(
        ["customer_id", "name", "email"]
    )

    assert len(results) == 1
    assert results[0]["customers_saved"] == 2

    assert not customer_file.exists()
    assert (service.processed_folder / "customers.csv").exists()
    assert (service.archive_folder / "customers.csv").exists()

    customers = service.database_manager.get_customers()

    assert customers == [
        (1, "Ali", "ali@example.com"),
        (2, "Sara", "sara@example.com"),
    ]


def test_automation_ignores_unsupported_files(tmp_path):
    """Test that unsupported files are not processed."""
    service = create_test_service(tmp_path)

    unsupported_file = service.input_folder / "notes.txt"

    unsupported_file.write_text(
        "This file should be ignored.",
        encoding="utf-8",
    )

    results = service.process_pending_files(
        ["customer_id", "name", "email"]
    )

    assert results == []
    assert unsupported_file.exists()


def test_automation_generates_report(tmp_path):
    """Test that successful automation generates a sales report."""
    service = create_test_service(tmp_path)

    customer_file = service.input_folder / "customers.csv"

    customer_file.write_text(
        "customer_id,name,email\n"
        "1,Ali,ali@example.com\n",
        encoding="utf-8",
    )

    current_directory = Path.cwd()

    try:
        import os

        os.chdir(tmp_path)

        results = service.process_pending_files(
            ["customer_id", "name", "email"]
        )

        report_path = tmp_path / "reports" / "sales_report.txt"

        assert len(results) == 1
        assert results[0]["report_generated"] == str(
            Path("reports/sales_report.txt")
        )

        assert report_path.exists()

        report_text = report_path.read_text(
            encoding="utf-8"
        )

        assert "BUSINESS SALES REPORT" in report_text
        assert "Total Orders: 0" in report_text

    finally:
        os.chdir(current_directory)
