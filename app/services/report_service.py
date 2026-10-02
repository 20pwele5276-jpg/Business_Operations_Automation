
from app.models.report import Report


class ReportService:
    """Handles business operations related to reports."""

    def create_report(self, report_id, title, content):
        """Create and return a validated report."""
        return Report(report_id, title, content)

    def generate_report(self, report):
        """Return the formatted report."""
        return report.generate()

