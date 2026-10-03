from app.exceptions.app_exceptions import ValidationError
from app.processors.data_cleaner import DataCleaner
from app.processors.data_validator import DataValidator
from app.utils.logger import AppLogger


class BusinessDataProcessor:
    """Validates and cleans business data rows."""

    def __init__(self):
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.logger = AppLogger()

    def process_rows(self, rows, required_fields):
        """Clean valid rows and report rows with validation errors."""
        valid_rows = []
        invalid_rows = []

        for row in rows:
            try:
                cleaned_row = self.cleaner.clean_row(row)

                missing_fields = self.validator.validate_required_fields(
                    cleaned_row,
                    required_fields,
                )

                if missing_fields:
                    raise ValidationError(
                        f"Missing required fields: {', '.join(missing_fields)}"
                    )

                valid_rows.append(cleaned_row)

            except ValidationError as error:
                self.logger.warning(f"Invalid row skipped: {error}")

                invalid_rows.append(
                    {
                        "row": row,
                        "error": str(error),
                    }
                )

            except Exception as error:
                self.logger.error(f"Unexpected processing error: {error}")

                invalid_rows.append(
                    {
                        "row": row,
                        "error": "Unexpected processing error",
                    }
                )

        return valid_rows, invalid_rows
