import pandas as pd

from app.processors.csv_processor import CSVProcessor
from app.processors.data_cleaner import DataCleaner
from app.processors.data_validator import DataValidator
from app.processors.json_processor import JSONProcessor


def test_csv_processor_write_and_read(tmp_path):
    processor = CSVProcessor()

    file_path = tmp_path / "customers.csv"

    rows = [
        {
            "customer_id": "1",
            "name": "Ali",
            "email": "ali@example.com",
        }
    ]

    fieldnames = [
        "customer_id",
        "name",
        "email",
    ]

    processor.write_file(
        file_path,
        rows,
        fieldnames,
    )

    result = processor.read_file(file_path)

    assert result == rows


def test_csv_processor_validate_columns(tmp_path):
    processor = CSVProcessor()

    file_path = tmp_path / "customers.csv"

    file_path.write_text(
        "customer_id,name\n1,Ali\n",
        encoding="utf-8",
    )

    missing_columns = processor.validate_columns(
        file_path,
        ["customer_id", "name", "email"],
    )

    assert missing_columns == ["email"]


def test_json_processor_write_and_read(tmp_path):
    processor = JSONProcessor()

    file_path = tmp_path / "products.json"

    data = [
        {
            "product_id": 1,
            "name": "Mouse",
            "price": 1000,
        }
    ]

    processor.write_file(
        file_path,
        data,
    )

    result = processor.read_file(file_path)

    assert result == data


def test_json_processor_validate_valid_file(tmp_path):
    processor = JSONProcessor()

    file_path = tmp_path / "valid.json"

    file_path.write_text(
        '[{"id": 1}]',
        encoding="utf-8",
    )

    assert processor.validate_file(file_path) is True


def test_json_processor_validate_invalid_file(tmp_path):
    processor = JSONProcessor()

    file_path = tmp_path / "invalid.json"

    file_path.write_text(
        "{invalid json}",
        encoding="utf-8",
    )

    assert processor.validate_file(file_path) is False


def test_data_cleaner_removes_extra_spaces():
    cleaner = DataCleaner()

    result = cleaner.clean_text(
        "   Ali    Khan   "
    )

    assert result == "Ali Khan"


def test_data_cleaner_handles_none():
    cleaner = DataCleaner()

    assert cleaner.clean_text(None) == ""


def test_data_cleaner_cleans_row():
    cleaner = DataCleaner()

    row = {
        "name": "   Ali    Khan ",
        "email": " ali@example.com ",
        "age": 22,
    }

    result = cleaner.clean_row(row)

    assert result == {
        "name": "Ali Khan",
        "email": "ali@example.com",
        "age": 22,
    }


def test_data_validator_required_fields():
    validator = DataValidator()

    row = {
        "customer_id": "1",
        "name": "",
        "email": "ali@example.com",
    }

    result = validator.validate_required_fields(
        row,
        ["customer_id", "name", "email"],
    )

    assert result == ["name"]


def test_data_validator_valid_email():
    validator = DataValidator()

    assert validator.is_valid_email(
        "ali@example.com"
    ) is True


def test_data_validator_invalid_email():
    validator = DataValidator()

    assert validator.is_valid_email(
        "invalid-email"
    ) is False


def test_data_validator_valid_row():
    validator = DataValidator()

    row = {
        "email": "ali@example.com",
        "price": "1500",
        "quantity": "2",
        "total_amount": "3000",
        "amount": "3000",
    }

    assert validator.validate_row(row) == []


def test_data_validator_negative_price():
    validator = DataValidator()

    row = {
        "price": "-500",
    }

    errors = validator.validate_row(row)

    assert "Price cannot be negative" in errors


def test_data_validator_invalid_price():
    validator = DataValidator()

    row = {
        "price": "abc",
    }

    errors = validator.validate_row(row)

    assert "Price must be a valid number" in errors


def test_data_validator_invalid_quantity():
    validator = DataValidator()

    row = {
        "quantity": "abc",
    }

    errors = validator.validate_row(row)

    assert "Quantity must be a valid integer" in errors


def test_data_validator_zero_quantity():
    validator = DataValidator()

    row = {
        "quantity": "0",
    }

    errors = validator.validate_row(row)

    assert "Quantity must be greater than zero" in errors


def test_data_validator_negative_total():
    validator = DataValidator()

    row = {
        "total_amount": "-100",
    }

    errors = validator.validate_row(row)

    assert "Total amount cannot be negative" in errors


def test_data_validator_invalid_payment_amount():
    validator = DataValidator()

    row = {
        "amount": "abc",
    }

    errors = validator.validate_row(row)

    assert "Payment amount must be a valid number" in errors
