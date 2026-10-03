
import time

import schedule

from app.automation.backup_service import BackupService
from app.utils.logger import AppLogger


class AutomationScheduler:
    """Schedules recurring automation tasks."""

    def __init__(self):
        self.backup_service = BackupService()
        self.logger = AppLogger()

    def backup_database(self):
        """Run the database backup task."""
        try:
            backup_file = self.backup_service.backup_database()

            self.logger.info(
                f"Scheduled backup completed: {backup_file.name}"
            )

        except Exception as error:
            self.logger.error(
                f"Scheduled backup failed: {error}"
            )

    def setup_schedule(self, interval_minutes=1440):
        """Schedule a daily database backup."""
        schedule.every(interval_minutes).minutes.do(
            self.backup_database
        )

        self.logger.info(
            f"Database backup scheduled every {interval_minutes} minute(s)."
        )

    def run(self):
        """Keep the scheduler running and execute pending tasks."""
        self.logger.info("Automation scheduler started.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Automation scheduler stopped.")
