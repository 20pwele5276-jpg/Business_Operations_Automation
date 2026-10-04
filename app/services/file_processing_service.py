
from pathlib import Path

import pandas as pd

from app.exceptions.app_exceptions import FileProcessingError
from app.processors.business_data_processor import BusinessDataProcessor
from app.processors.csv_processor import CSVProcessor
from app.processors.excel_processor import ExcelProcessor
from app.processors.json_processor import JSONProcessor
from app.utils.logger import AppLogger


class FileProcessingService:
    """Coordinates reading, validating, cleaning, and saving business files."""

    def __init__(self):
        self.csv_processor = CSVProcessor()
        self.json_processor = JSONProcessor()
        self.excel_processor = ExcelProcessor()
        self.data_processor = BusinessDataProcessor()
        self.logger = AppLogger()

    def process_file(self, input_path, output_path, required_fields):
        """Process a supported business file and save the cleaned result."""

        input_path = Path(input_path)
        output_path = Path(output_path)

        try:
            if not input_path.is_file():
                raise FileProcessingError(
                    f"Input file does not exist: {input_path}"
                )

            extension = input_path.suffix.lower()

            if extension == ".csv":
                rows = self.csv_processor.read_file(input_path)

                valid_rows, invalid_rows = self.data_processor.process_rows(
                    rows,
                    required_fields,
                )

                fieldnames = (
                    list(rows[0].keys())
                    if rows
                    else required_fields
                )

                self.csv_processor.write_file(
                    output_path,
                    valid_rows,
                    fieldnames,
                )

            elif extension == ".json":
                data = self.json_processor.read_file(input_path)

                if not isinstance(data, list):
                    raise FileProcessingError(
                        "JSON business data must contain a list of records."
                    )

                valid_rows, invalid_rows = self.data_processor.process_rows(
                    data,
                    required_fields,
                )

                self.json_processor.write_file(
                    output_path,
                    valid_rows,
                )

            elif extension in [".xlsx", ".xls"]:
                data = self.excel_processor.read_file(input_path)

                rows = data.to_dict(orient="records")

                valid_rows, invalid_rows = self.data_processor.process_rows(
                    rows,
                    required_fields,
                )

                cleaned_data = pd.DataFrame(valid_rows)

                self.excel_processor.write_file(
                    output_path,
                    cleaned_data,
                )

            else:
                raise FileProcessingError(
                    f"Unsupported file type: {extension}"
                )

            self.logger.info(
                f"File processed successfully: {input_path.name}"
            )

            return {
                "input_file": str(input_path),
                "output_file": str(output_path),
                "valid_rows": len(valid_rows),
                "invalid_rows": len(invalid_rows),
                "invalid_records": invalid_rows,
            }

        except FileProcessingError:
            raise

        except Exception as error:
            self.logger.error(
                f"Failed to process file {input_path.name}: {error}"
            )

            raise FileProcessingError(
                f"Could not process file: {input_path.name}"
            ) from error
