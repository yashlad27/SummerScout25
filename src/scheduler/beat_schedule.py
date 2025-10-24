"""Celery Beat schedule configuration."""

from celery.schedules import crontab

# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    # Run full tracker every 4 hours
    "run-job-tracker-every-4hrs": {
        "task": "tasks.run_job_tracker",
        "schedule": crontab(minute=0, hour="*/4"),  # Every 4 hours (at 0, 4, 8, 12, 16, 20)
        "options": {
            "expires": 14400,  # Expire after 4 hours
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
