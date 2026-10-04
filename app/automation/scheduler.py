
import time

import schedule

from app.automation.automation_service import AutomationService
from app.utils.logger import AppLogger


class AutomationScheduler:
    """Schedules recurring business automation tasks."""

    def __init__(self, automation_service=None):
        self.automation_service = (
            automation_service or AutomationService()
        )
        self.logger = AppLogger()

    def run_business_automation(self):
        """Process pending files using the automation workflow."""

        try:
            results = (
                self.automation_service.process_pending_files()
            )

            self.logger.info(
                "Scheduled business automation completed. "
                f"Processed {len(results)} file(s)."
            )

            return results

        except Exception as error:
            self.logger.error(
                f"Scheduled business automation failed: {error}"
            )

            return []

    def setup_schedule(self, interval_minutes=1440):
        """Schedule recurring business automation."""

        schedule.every(
            interval_minutes
        ).minutes.do(
            self.run_business_automation
        )

        self.logger.info(
            "Business automation scheduled every "
            f"{interval_minutes} minute(s)."
        )

    def clear_schedule(self):
        """Remove all scheduled tasks."""

        schedule.clear()

        self.logger.info(
            "All scheduled tasks cleared."
        )

    def run_pending(self):
        """Run scheduled tasks that are currently due."""

        schedule.run_pending()

    def run(self, check_interval=1):
        """Keep the scheduler running continuously."""

        self.logger.info(
            "Automation scheduler started."
        )

        try:
            while True:
                self.run_pending()
                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info(
                "Automation scheduler stopped."
            )
