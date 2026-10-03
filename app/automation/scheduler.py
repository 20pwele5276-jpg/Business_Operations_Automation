
import time

import schedule

from app.automation.automation_service import AutomationService
from app.automation.backup_service import BackupService
from app.utils.logger import AppLogger


class AutomationScheduler:
    """Schedules recurring business automation tasks."""

    def __init__(self):
        self.automation_service = AutomationService()
        self.backup_service = BackupService()
        self.logger = AppLogger()

    def run_business_automation(self):
        """Process pending files and generate the latest report."""
        try:
            results = self.automation_service.process_pending_files()

            self.logger.info(
                f"Scheduled business automation completed. "
                f"Processed {len(results)} file(s)."
            )

        except Exception as error:
            self.logger.error(
                f"Scheduled business automation failed: {error}"
            )

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
        """Schedule recurring business automation and database backups."""
        schedule.every(interval_minutes).minutes.do(
            self.run_business_automation
        )

        schedule.every(interval_minutes).minutes.do(
            self.backup_database
        )

        self.logger.info(
            "Business automation and database backup "
            f"scheduled every {interval_minutes} minute(s)."
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
