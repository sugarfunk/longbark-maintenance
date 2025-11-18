"""Celery application configuration"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "longbark",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.monitoring_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Configure periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "check-all-sites-every-5-minutes": {
        "task": "app.tasks.monitoring_tasks.check_all_sites",
        "schedule": 300.0,  # 5 minutes (default interval)
    },
    "cleanup-old-data-daily": {
        "task": "app.tasks.monitoring_tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
