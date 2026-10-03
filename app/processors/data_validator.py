
class DataValidator:
    """Validates basic business data."""

    def validate_required_fields(self, row, required_fields):
        """Return missing required fields from a data row."""
        missing_fields = []

        for field in required_fields:
            value = row.get(field)

            if value is None or str(value).strip() == "":
                missing_fields.append(field)

        return missing_fields

    def is_valid_email(self, email):
        """Check whether an email contains the basic required format."""
        if not email:
            return False

        return "@" in email and "." in email.split("@")[-1]

