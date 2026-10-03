
class DataCleaner:
    """Cleans basic business data."""

    def clean_text(self, value):
        """Remove extra spaces from text."""
        if value is None:
            return ""

        return " ".join(str(value).strip().split())

    def clean_row(self, row):
        """Clean text values in a data row."""
        cleaned_row = {}

        for field, value in row.items():
            if isinstance(value, str):
                cleaned_row[field] = self.clean_text(value)
            else:
                cleaned_row[field] = value

        return cleaned_row
