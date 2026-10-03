import logging
from pathlib import Path


class AppLogger:
    """Provides centralized logging for the application."""

    def __init__(self, log_file="logs/app.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("business_automation")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(
                self.log_file,
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )

            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message):
        """Record an informational event."""
        self.logger.info(message)

    def warning(self, message):
        """Record a warning."""
        self.logger.warning(message)

    def error(self, message):
        """Record an error."""
        self.logger.error(message)
