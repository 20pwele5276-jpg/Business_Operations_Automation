
from app.processors.data_cleaner import DataCleaner
from app.processors.data_validator import DataValidator


class BusinessDataProcessor:
    """Validates and cleans business data rows."""

    def __init__(self):
        self.cleaner = DataCleaner()
        self.validator = DataValidator()

    def process_rows(self, rows, required_fields):
        """Clean valid rows and report rows with missing required fields."""
        valid_rows = []
        invalid_rows = []

        for row in rows:
            cleaned_row = self.cleaner.clean_row(row)
            missing_fields = self.validator.validate_required_fields(
                cleaned_row,
                required_fields,
            )

            if missing_fields:
                invalid_rows.append(
                    {
                        "row": cleaned_row,
                        "missing_fields": missing_fields,
                    }
                )
            else:
                valid_rows.append(cleaned_row)

        return valid_rows, invalid_rows

