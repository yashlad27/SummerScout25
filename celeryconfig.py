"""
Celery Configuration File for Job Tracker

This file contains all Celery configuration including the automatic schedule.
"""

from celery.schedules import crontab

# ===========================
# CELERY CONFIGURATION
# ===========================

# Broker and Backend Settings
broker_url = 'redis://redis:6379/0'
result_backend = 'redis://redis:6379/0'

# Serialization
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'

# Timezone
timezone = 'UTC'
enable_utc = True

# Task Settings
task_track_started = True
task_time_limit = 3600  # 1 hour max per task
worker_prefetch_multiplier = 1

# ===========================
# AUTOMATIC SCHEDULE
# ===========================

beat_schedule = {
    # Main scraper - runs every 4 hours
    'scrape-all-companies-every-4-hours': {
        'task': 'tasks.run_job_tracker',
        'schedule': crontab(minute=0, hour='*/4'),  # Runs at: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
        'options': {
            'expires': 14400,  # Expire after 4 hours
        },
    },
    
    # Example: Scrape high-priority companies more frequently
    # Uncomment to enable
    #
    # 'scrape-google-every-hour': {
    #     'task': 'tasks.run_job_tracker_for_company',
    #     'schedule': crontab(minute=0),  # Every hour
    #     'args': ('Google',),
    # },
    #
    # 'scrape-microsoft-every-hour': {
    #     'task': 'tasks.run_job_tracker_for_company',
    #     'schedule': crontab(minute=0),  # Every hour
    #     'args': ('Microsoft',),
    # },
}

# ===========================
# SCHEDULE EXAMPLES
# ===========================

# Uncomment any of these to customize your scraping schedule:

# Every 2 hours
# beat_schedule['scrape-every-2-hours'] = {
#     'task': 'tasks.run_job_tracker',
#     'schedule': crontab(minute=0, hour='*/2'),
# }

# Every 6 hours
# beat_schedule['scrape-every-6-hours'] = {
#     'task': 'tasks.run_job_tracker',
#     'schedule': crontab(minute=0, hour='*/6'),
# }

# Daily at specific time (9 AM)
# beat_schedule['scrape-daily-9am'] = {
#     'task': 'tasks.run_job_tracker',
#     'schedule': crontab(minute=0, hour=9),
# }

# Twice daily (9 AM and 5 PM)
# beat_schedule['scrape-twice-daily'] = {
#     'task': 'tasks.run_job_tracker',
#     'schedule': crontab(minute=0, hour='9,17'),
# }

# Weekdays only at 9 AM
# beat_schedule['scrape-weekdays'] = {
#     'task': 'tasks.run_job_tracker',
#     'schedule': crontab(minute=0, hour=9, day_of_week='1-5'),
# }

# Specific companies on different schedules
# beat_schedule['scrape-faang-every-2-hours'] = {
#     'task': 'tasks.run_job_tracker_for_company',
#     'schedule': crontab(minute=0, hour='*/2'),
#     'args': ('Google',),
# }
