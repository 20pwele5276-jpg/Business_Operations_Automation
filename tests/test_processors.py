
import pandas as pd

from app.processors.business_data_processor import BusinessDataProcessor
from app.processors.csv_processor import CSVProcessor
from app.processors.data_cleaner import DataCleaner
from app.processors.data_validator import DataValidator
from app.processors.excel_processor import ExcelProcessor
from app.processors.json_processor import JSONProcessor


def test_csv_read_and_write(tmp_path):
    """Test that CSV data can be written and read correctly."""
    processor = CSVProcessor()
    file_path = tmp_path / "customers.csv"

    rows = [
        {"name": "Ali", "email": "ali@example.com"},
        {"name": "Sara", "email": "sara@example.com"},
    ]

    processor.write_file(
        file_path,
        rows,
        ["name", "email"],
    )

    result = processor.read_file(file_path)

    assert result == rows


def test_csv_validate_columns(tmp_path):
    """Test that missing CSV columns are detected."""
    processor = CSVProcessor()
    file_path = tmp_path / "customers.csv"

    file_path.write_text(
        "name\nAli\n",
        encoding="utf-8",
    )

    missing_columns = processor.validate_columns(
        file_path,
        ["name", "email"],
    )

    assert missing_columns == ["email"]


def test_json_read_write_and_validate(tmp_path):
    """Test JSON writing, reading, and validation."""
    processor = JSONProcessor()
    file_path = tmp_path / "customers.json"

    data = [
        {"name": "Ali", "email": "ali@example.com"},
    ]

    processor.write_file(file_path, data)

    assert processor.read_file(file_path) == data
    assert processor.validate_file(file_path) is True


def test_json_invalid_file(tmp_path):
    """Test that invalid JSON is detected."""
    processor = JSONProcessor()
    file_path = tmp_path / "invalid.json"

    file_path.write_text(
        "{invalid json}",
        encoding="utf-8",
    )

    assert processor.validate_file(file_path) is False


def test_excel_read_and_write(tmp_path):
    """Test that Excel data can be written and read correctly."""
    processor = ExcelProcessor()
    file_path = tmp_path / "products.xlsx"

    data = pd.DataFrame(
        [
            {"name": "Laptop", "price": 150000},
            {"name": "Mouse", "price": 2500},
        ]
    )

    processor.write_file(file_path, data)

    result = processor.read_file(file_path)

    assert result.to_dict(orient="records") == (
        data.to_dict(orient="records")
    )


def test_data_validator_required_fields():
    """Test detection of missing required fields."""
    validator = DataValidator()

    row = {
        "name": "Ali",
        "email": "",
    }

    missing_fields = validator.validate_required_fields(
        row,
        ["name", "email"],
    )

    assert missing_fields == ["email"]


def test_data_validator_email():
    """Test basic email validation."""
    validator = DataValidator()

    assert validator.is_valid_email("ali@example.com") is True
    assert validator.is_valid_email("invalid-email") is False


def test_data_cleaner():
    """Test that extra spaces are removed from text."""
    cleaner = DataCleaner()

    row = {
        "name": "  Ali   Khan  ",
        "email": " ali@example.com ",
    }

    cleaned_row = cleaner.clean_row(row)

    assert cleaned_row == {
        "name": "Ali Khan",
        "email": "ali@example.com",
    }


def test_business_data_processor():
    """Test that valid rows are accepted and invalid rows are rejected."""
    processor = BusinessDataProcessor()

    rows = [
        {
            "name": "  Ali  ",
            "email": "ali@example.com",
        },
        {
            "name": "",
            "email": "invalid-email",
        },
    ]

    valid_rows, invalid_rows = processor.process_rows(
        rows,
        ["name", "email"],
    )

    assert len(valid_rows) == 1
    assert valid_rows[0]["name"] == "Ali"
    assert len(invalid_rows) == 1
