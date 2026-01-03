"""
Celery task queue configuration
"""
from celery import Celery
from celery.schedules import crontab

from src.config import settings

# Initialize Celery app
celery_app = Celery(
    "trainingplan",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.celery_timezone,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "sync-garmin-activities": {
        "task": "src.tasks.sync_garmin_activities",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
    },
    "calculate-training-load": {
        "task": "src.tasks.calculate_training_load",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}


# Example task
@celery_app.task(name="src.tasks.sync_garmin_activities")
def sync_garmin_activities():
    """
    Sync activities from Garmin Connect for all users.
    This is a placeholder that will be implemented in Phase 3.
    """
    print("Syncing Garmin activities...")
    # Implementation will be added in Phase 3
    return {"status": "success", "message": "Garmin sync completed"}


@celery_app.task(name="src.tasks.calculate_training_load")
def calculate_training_load():
    """
    Calculate training load metrics (CTL, ATL, TSB) for all users.
    This is a placeholder that will be implemented in Phase 5.
    """
    print("Calculating training load...")
    # Implementation will be added in Phase 5
    return {"status": "success", "message": "Training load calculation completed"}
