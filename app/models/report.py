
class Report:
    """Represents a business report."""

    def __init__(self, report_id, title, content):
        if not title.strip():
            raise ValueError("Report title cannot be empty.")

        self.report_id = report_id
        self.title = title
        self.content = content

    def generate(self):
        """Return the formatted report."""
        return f"Report ID: {self.report_id}\nTitle: {self.title}\n\n{self.content}"

    def __str__(self):
        """Return a readable representation of the report."""
        return f"Report {self.report_id}: {self.title}"

