"""Celery Beat schedule configuration."""

from celery.schedules import crontab

# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    # Run full tracker every 30 minutes
    "run-job-tracker-every-30min": {
        "task": "tasks.run_job_tracker",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
        "options": {
            "expires": 1800,  # Expire after 30 minutes
        },
    },
    
    # You can add more granular schedules here
    # For example, run specific companies more frequently:
    #
    # "run-citadel-every-30min": {
    #     "task": "tasks.run_job_tracker_for_company",
    #     "schedule": crontab(minute="*/30"),
    #     "args": ("Citadel",),
    # },
}
