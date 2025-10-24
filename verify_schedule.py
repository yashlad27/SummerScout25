#!/usr/bin/env python3
"""
Verify Celery Beat Schedule Configuration

This script checks if the Celery Beat schedule is properly configured
and shows when the next scrape will run.
"""

from datetime import datetime, timedelta
from celery.schedules import crontab

def get_next_run_time(cron_schedule):
    """Calculate when a crontab schedule will next run."""
    now = datetime.utcnow()
    
    # Get the next minute that matches
    next_run = now.replace(second=0, microsecond=0)
    
    # Check next 24 hours for matching time
    for _ in range(24 * 60):
        next_run += timedelta(minutes=1)
        
        if cron_schedule.hour and next_run.hour not in cron_schedule.hour:
            continue
        if cron_schedule.minute and next_run.minute not in cron_schedule.minute:
            continue
        
        return next_run
    
    return None

def main():
    print("=" * 70)
    print("🔍 CELERY BEAT SCHEDULE VERIFICATION")
    print("=" * 70)
    print()
    
    try:
        import celeryconfig
        
        print("✅ celeryconfig.py found and loaded")
        print()
        
        if hasattr(celeryconfig, 'beat_schedule'):
            schedule = celeryconfig.beat_schedule
            print(f"📊 Found {len(schedule)} scheduled tasks:")
            print()
            
            for task_name, task_config in schedule.items():
                print(f"📋 Task: {task_name}")
                print(f"   └─ Runs: {task_config['task']}")
                
                if 'schedule' in task_config:
                    sched = task_config['schedule']
                    if isinstance(sched, crontab):
                        print(f"   └─ Schedule: {sched}")
                        
                        # Show human-readable schedule
                        if sched.hour == '*/4':
                            print(f"   └─ Frequency: Every 4 hours")
                            print(f"   └─ Run times: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC")
                        elif sched.hour == '*/2':
                            print(f"   └─ Frequency: Every 2 hours")
                        elif sched.hour == '*/6':
                            print(f"   └─ Frequency: Every 6 hours")
                        else:
                            print(f"   └─ Frequency: Custom crontab")
                
                if 'args' in task_config:
                    print(f"   └─ Arguments: {task_config['args']}")
                
                print()
            
            print("=" * 70)
            print("⏰ NEXT SCHEDULED RUNS")
            print("=" * 70)
            print()
            
            now = datetime.utcnow()
            print(f"Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            for task_name, task_config in schedule.items():
                if 'schedule' in task_config and isinstance(task_config['schedule'], crontab):
                    sched = task_config['schedule']
                    
                    # Calculate next run for 4-hour schedule
                    if sched.hour == '*/4':
                        current_hour = now.hour
                        next_hour = ((current_hour // 4) + 1) * 4
                        if next_hour >= 24:
                            next_hour = 0
                            next_run = now.replace(hour=next_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
                        else:
                            next_run = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
                            if next_run < now:
                                next_run += timedelta(hours=4)
                        
                        time_until = next_run - now
                        hours = int(time_until.total_seconds() // 3600)
                        minutes = int((time_until.total_seconds() % 3600) // 60)
                        
                        print(f"📅 {task_name}:")
                        print(f"   └─ Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                        print(f"   └─ Time until: {hours}h {minutes}m")
                        print()
            
            print("=" * 70)
            print("✅ CONFIGURATION VALID")
            print("=" * 70)
            print()
            print("To start the scheduler:")
            print("  docker-compose up -d beat worker")
            print()
            print("To monitor the scheduler:")
            print("  docker logs -f job_tracker_beat")
            print()
            
        else:
            print("❌ Error: beat_schedule not found in celeryconfig.py")
            return 1
    
    except ImportError as e:
        print(f"❌ Error: Could not import celeryconfig.py")
        print(f"   {str(e)}")
        print()
        print("Make sure celeryconfig.py is in the project root directory.")
        return 1
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
