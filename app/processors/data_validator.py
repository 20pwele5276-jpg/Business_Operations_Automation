
class DataValidator:
    """Validates business data before it enters the system."""

    def validate_required_fields(self, row, required_fields):
        """Return required fields that are missing or empty."""

        missing_fields = []

        for field in required_fields:
            value = row.get(field)

            if value is None or str(value).strip() == "":
                missing_fields.append(field)

        return missing_fields

    def is_valid_email(self, email):
        """Check whether an email has a basic valid format."""

        if not email:
            return False

        email = str(email).strip()

        if "@" not in email:
            return False

        local_part, domain = email.rsplit("@", 1)

        if not local_part or "." not in domain:
            return False

        return True

    def validate_row(self, row):
        """Return validation errors for a business data row."""

        errors = []

        # Validate email fields when they are present.
        if "email" in row:
            if not self.is_valid_email(row["email"]):
                errors.append("Invalid email format")

        # Validate product price.
        if "price" in row:
            try:
                price = float(row["price"])

                if price < 0:
                    errors.append("Price cannot be negative")

            except (ValueError, TypeError):
                errors.append("Price must be a valid number")

        # Validate order quantity.
        if "quantity" in row:
            try:
                quantity = int(row["quantity"])

                if quantity <= 0:
                    errors.append("Quantity must be greater than zero")

            except (ValueError, TypeError):
                errors.append("Quantity must be a valid integer")

        # Validate invoice total.
        if "total_amount" in row:
            try:
                total_amount = float(row["total_amount"])

                if total_amount < 0:
                    errors.append("Total amount cannot be negative")

            except (ValueError, TypeError):
                errors.append("Total amount must be a valid number")

        # Validate payment amount.
        if "amount" in row:
            try:
                amount = float(row["amount"])

                if amount <= 0:
                    errors.append("Payment amount must be greater than zero")

            except (ValueError, TypeError):
                errors.append("Payment amount must be a valid number")

        return errors
