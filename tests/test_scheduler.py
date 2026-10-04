
import schedule

from app.automation.scheduler import AutomationScheduler


class FakeAutomationService:
    """Provides a simple fake service for scheduler testing."""

    def __init__(self):
        self.called = False

    def process_pending_files(self):
        self.called = True
        return ["customers.csv"]


def test_scheduler_runs_business_automation():
    """Test that the scheduler runs the automation service."""

    fake_service = FakeAutomationService()

    scheduler = AutomationScheduler(
        automation_service=fake_service
    )

    results = scheduler.run_business_automation()

    assert fake_service.called is True
    assert results == ["customers.csv"]


def test_scheduler_creates_schedule():
    """Test that the scheduler creates a recurring task."""

    schedule.clear()

    fake_service = FakeAutomationService()

    scheduler = AutomationScheduler(
        automation_service=fake_service
    )

    scheduler.setup_schedule(
        interval_minutes=60
    )

    assert len(schedule.get_jobs()) == 1

    schedule.clear()


def test_scheduler_clears_schedule():
    """Test that scheduled tasks can be removed."""

    schedule.clear()

    fake_service = FakeAutomationService()

    scheduler = AutomationScheduler(
        automation_service=fake_service
    )

    scheduler.setup_schedule(
        interval_minutes=60
    )

    scheduler.clear_schedule()

    assert len(schedule.get_jobs()) == 0
