
from app.automation.scheduler import AutomationScheduler


def main():
    """Start the Business Operations Automation Platform."""
    print("Business Operations Automation Platform is starting...")

    scheduler = AutomationScheduler()
    scheduler.setup_schedule()

    print("Daily database backup scheduler is running.")
    print("Press Ctrl+C to stop the application.")

    scheduler.run()


if __name__ == "__main__":
    main()
