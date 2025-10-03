import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neuroscan.settings")

app = Celery("neuroscan")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

try:
    from celery.schedules import crontab
    app.conf.beat_schedule = {
        "process-pending-assessments-hourly": {
            "task": "mental_health_app.tasks.process_pending_assessments",
            "schedule": crontab(minute=0, hour="*"),
        },
        "daily-cleanup": {
            "task": "mental_health_app.tasks.daily_cleanup",
            "schedule": crontab(minute=0, hour=0),
        },
    }
except Exception:
    pass
