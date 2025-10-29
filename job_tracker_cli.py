#!/usr/bin/env python3
"""Interactive CLI for Job Tracker - Run scrapes, view results, and manage job data."""

import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.database import get_db_context
from src.core.models import Job
from sqlalchemy import func, and_


class JobTrackerCLI:
    """Interactive command-line interface for job tracking."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.exports_dir = self.project_root / "exports"
        self.master_log = self.project_root / "MASTER_JOB_LOG.csv"
        
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Print application header with ASCII art."""
        print("\033[1;36m")  # Cyan color
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║      ██╗ ██████╗ ██████╗     ████████╗██████╗  █████╗  ██████╗██╗  ██╗      ║
║      ██║██╔═══██╗██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝      ║
║      ██║██║   ██║██████╔╝       ██║   ██████╔╝███████║██║     █████╔╝       ║
║ ██   ██║██║   ██║██╔══██╗       ██║   ██╔══██╗██╔══██║██║     ██╔═██╗       ║
║ ╚█████╔╝╚██████╔╝██████╔╝       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗      ║
║  ╚════╝  ╚═════╝ ╚═════╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝      ║
║                                                                               ║
║               🎯 Internship Tracking & Management System 🎯                  ║
║                     Masters Students | Summer 2026                           ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """)
        print("\033[0m")  # Reset color
    
    def print_menu(self):
        """Print main menu options."""
        print("\033[1;33m")  # Yellow/Gold color
        print("""
┌──────────────────────────────────────────────────────────────────────────────┐
│                              📋  MAIN MENU                                   │
└──────────────────────────────────────────────────────────────────────────────┘
        """)
        print("\033[0m")  # Reset color
        
        # Actions section
        print("\033[1;32m")  # Green for actions
        print("  ╔══════════════════════════════════════════════════════════════════════╗")
        print("  ║                         🎬  ACTIONS                                  ║")
        print("  ╠══════════════════════════════════════════════════════════════════════╣")
        print("\033[0m")
        print("  ║  \033[1;36m1.\033[0m 🚀 Run Full Scrape (All 327 Companies)                          ║")
        print("  ║  \033[1;36m2.\033[0m 🎯 Run Single Company Scrape                                    ║")
        print("  ╚══════════════════════════════════════════════════════════════════════╝")
        
        # Analytics section
        print("\n\033[1;35m")  # Magenta for analytics
        print("  ╔══════════════════════════════════════════════════════════════════════╗")
        print("  ║                       📊  ANALYTICS & REPORTS                        ║")
        print("  ╠══════════════════════════════════════════════════════════════════════╣")
        print("\033[0m")
        print("  ║  \033[1;36m3.\033[0m 📊 View Today's Statistics                                      ║")
        print("  ║  \033[1;36m4.\033[0m 🆕 View New Jobs (Last 24 Hours)                                ║")
        print("  ║  \033[1;36m5.\033[0m 📈 View All-Time Statistics                                     ║")
        print("  ║  \033[1;36m6.\033[0m 📁 View Recent Export Files                                     ║")
        print("  ╚══════════════════════════════════════════════════════════════════════╝")
        
        # Search & Export section
        print("\n\033[1;34m")  # Blue for search
        print("  ╔══════════════════════════════════════════════════════════════════════╗")
        print("  ║                      🔍  SEARCH & EXPORT                             ║")
        print("  ╠══════════════════════════════════════════════════════════════════════╣")
        print("\033[0m")
        print("  ║  \033[1;36m7.\033[0m 💾 Export Master Job Log (CSV)                                  ║")
        print("  ║  \033[1;36m8.\033[0m 🔍 Search Jobs by Keyword                                       ║")
        print("  ║  \033[1;36m9.\033[0m 🏢 View Jobs by Company                                         ║")
        print("  ╚══════════════════════════════════════════════════════════════════════╝")
        
        # Exit
        print("\n  \033[1;31m0. ❌ Exit Application\033[0m")
        print("\n" + "═" * 80)
    
    def run_full_scrape(self):
        """Run full batch scrape."""
        print("\n\033[1;32m")  # Green
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                     🚀  FULL SCRAPE - ALL COMPANIES                           ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print("\n  📊 Companies to scrape: \033[1;36m327\033[0m")
        print("  ⏱️  Estimated time: \033[1;33m30-60 minutes\033[0m")
        print("  📂 Output: Database + Exports + Master Log")
        
        confirm = input("\n  \033[1;33m⚠️  Proceed with full scrape? (y/n):\033[0m ").strip().lower()
        if confirm != 'y':
            print("\n  \033[1;31m❌ Cancelled.\033[0m")
            input("\n  Press Enter to continue...")
            return
        
        print("\n\033[1;36m")
        print("  ╔═══════════════════════════════════════════════════════════════════╗")
        print("  ║  ⏳  SCRAPING IN PROGRESS... Please wait...                       ║")
        print("  ╚═══════════════════════════════════════════════════════════════════╝")
        print("\033[0m\n")
        
        os.system("cd {} && ./scrape_batch.sh".format(self.project_root))
        
        print("\n\033[1;32m")
        print("  ╔═══════════════════════════════════════════════════════════════════╗")
        print("  ║  ✅  SCRAPE COMPLETE!                                             ║")
        print("  ╚═══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print("\n  \033[1;36m📂 Results saved to database and export files\033[0m")
        print("  \033[1;33m💡 Use Option 7 to export Master CSV Log\033[0m")
        
        input("\n  \033[1;32m✓\033[0m Press Enter to continue...")
    
    def run_single_scrape(self):
        """Run scrape for a single company."""
        print("\n\033[1;36m")  # Cyan
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                    🎯  SINGLE COMPANY SCRAPE                                  ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        company = input("\n  📝 Enter company name: ").strip()
        if not company:
            print("\n  \033[1;31m❌ No company name provided.\033[0m")
            input("\n  Press Enter to continue...")
            return
        
        print(f"\n\033[1;33m  ⏳ Scraping \033[1;36m{company}\033[1;33m...\033[0m\n")
        os.system(f"cd {self.project_root} && ./scrape.sh \"{company}\"")
        
        print("\n\033[1;32m  ✅ Scrape complete!\033[0m")
        print("  \033[1;36m📂 Results saved to database and export files\033[0m")
        print("  \033[1;33m💡 Use Option 7 to export Master CSV Log\033[0m")
        
        input("\n  \033[1;32m✓\033[0m Press Enter to continue...")
    
    def view_today_stats(self):
        """View statistics for jobs seen today."""
        print("\n\033[1;35m")  # Magenta
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                        📊  TODAY'S STATISTICS                                 ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        try:
            with get_db_context() as db:
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                
                # Jobs seen today
                jobs_today = db.query(Job).filter(
                    Job.last_seen_at >= today_start
                ).count()
                
                # New jobs today
                new_today = db.query(Job).filter(
                    Job.first_seen_at >= today_start
                ).count()
                
                # Updated jobs today
                updated_today = db.query(Job).filter(
                    and_(
                        Job.last_seen_at >= today_start,
                        Job.first_seen_at < today_start
                    )
                ).count()
                
                # Active jobs
                active_jobs = db.query(Job).filter(Job.is_active == True).count()
                
                # Companies scraped today
                companies_today = db.query(Job.company).filter(
                    Job.last_seen_at >= today_start
                ).distinct().count()
                
                print(f"\n  📅 Date: \033[1;36m{today.strftime('%A, %B %d, %Y')}\033[0m")
                print("\n  ┌────────────────────────────────────────────────────────────────────┐")
                print(f"  │  🔍 Jobs Processed Today:    \033[1;33m{jobs_today:>4}\033[0m                             │")
                print(f"  │  🆕 New Jobs Found:          \033[1;32m{new_today:>4}\033[0m                             │")
                print(f"  │  🔄 Jobs Updated:            \033[1;34m{updated_today:>4}\033[0m                             │")
                print(f"  │  ✅ Total Active Jobs:       \033[1;36m{active_jobs:>4}\033[0m                             │")
                print(f"  │  🏢 Companies Scraped:       \033[1;35m{companies_today:>4}\033[0m                             │")
                print("  └────────────────────────────────────────────────────────────────────┘")
                
                # Top companies with new jobs today
                if new_today > 0:
                    print("\n\033[1;33m  ╔═══════════════════════════════════════════════════════════════════╗\033[0m")
                    print("\033[1;33m  ║       🏆  TOP COMPANIES WITH NEW JOBS TODAY                       ║\033[0m")
                    print("\033[1;33m  ╚═══════════════════════════════════════════════════════════════════╝\033[0m")
                    
                    top_companies = db.query(
                        Job.company,
                        func.count(Job.id).label('count')
                    ).filter(
                        Job.first_seen_at >= today_start
                    ).group_by(
                        Job.company
                    ).order_by(
                        func.count(Job.id).desc()
                    ).limit(10).all()
                    
                    for i, (company, count) in enumerate(top_companies, 1):
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                        print(f"  {medal} \033[1;36m{company:<40}\033[0m \033[1;32m{count:>3} jobs\033[0m")
        
        except Exception as e:
            print(f"\n  \033[1;31m❌ Error fetching statistics: {e}\033[0m")
        
        input("\n  \033[1;32m✓\033[0m Press Enter to continue...")
    
    def view_new_jobs(self):
        """View new jobs from last 24 hours."""
        print("\n\033[1;32m")  # Green
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                     🆕  NEW JOBS (LAST 24 HOURS)                              ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        try:
            with get_db_context() as db:
                yesterday = datetime.now() - timedelta(days=1)
                
                new_jobs = db.query(Job).filter(
                    Job.first_seen_at >= yesterday
                ).order_by(
                    Job.first_seen_at.desc()
                ).all()
                
                if not new_jobs:
                    print("\n  \033[1;33m💤 No new jobs found in the last 24 hours.\033[0m")
                else:
                    print(f"\n  \033[1;32m✅ Found \033[1;36m{len(new_jobs)}\033[1;32m new jobs!\033[0m\n")
                    
                    for i, job in enumerate(new_jobs, 1):
                        print(f"\n  ┌{'─' * 76}┐")
                        print(f"  │ \033[1;33m#{i}\033[0m  🏢 \033[1;36m{job.company:<68}\033[0m│")
                        print(f"  ├{'─' * 76}┤")
                        title_display = job.title[:65] + "..." if len(job.title) > 65 else job.title
                        print(f"  │  📋 {title_display:<69}│")
                        print(f"  │  📍 {(job.location or 'Remote'):<69}│")
                        if job.category:
                            print(f"  │  🏷️  \033[1;35m{job.category:<68}\033[0m│")
                        date_str = job.first_seen_at.strftime('%Y-%m-%d %H:%M')
                        print(f"  │  📅 {date_str:<69}│")
                        print(f"  └{'─' * 76}┘")
        
        except Exception as e:
            print(f"\n  \033[1;31m❌ Error fetching new jobs: {e}\033[0m")
        
        input("\n  \033[1;32m✓\033[0m Press Enter to continue...")
    
    def view_all_time_stats(self):
        """View all-time statistics."""
        print("\n📈 All-Time Statistics")
        print("=" * 80)
        
        try:
            with get_db_context() as db:
                # Total jobs
                total_jobs = db.query(Job).count()
                active_jobs = db.query(Job).filter(Job.is_active == True).count()
                inactive_jobs = total_jobs - active_jobs
                
                # Companies tracked
                total_companies = db.query(Job.company).distinct().count()
                
                # Jobs by category
                categories = db.query(
                    Job.category,
                    func.count(Job.id).label('count')
                ).filter(
                    Job.is_active == True
                ).group_by(
                    Job.category
                ).order_by(
                    func.count(Job.id).desc()
                ).all()
                
                # Oldest and newest
                oldest = db.query(Job).order_by(Job.first_seen_at.asc()).first()
                newest = db.query(Job).order_by(Job.first_seen_at.desc()).first()
                
                print(f"📊 Total Jobs Ever Tracked:   {total_jobs}")
                print(f"✅ Currently Active:          {active_jobs}")
                print(f"❌ Inactive/Closed:           {inactive_jobs}")
                print(f"🏢 Companies Tracked:         {total_companies}")
                
                if oldest:
                    print(f"\n📅 First Job Tracked:         {oldest.first_seen_at.strftime('%Y-%m-%d')}")
                if newest:
                    print(f"📅 Most Recent Job:           {newest.first_seen_at.strftime('%Y-%m-%d')}")
                
                print(f"\n🏷️  Jobs by Category:")
                print("-" * 80)
                for category, count in categories[:10]:
                    cat_name = category or "Uncategorized"
                    print(f"  • {cat_name}: {count} jobs")
                
                # Top companies
                print(f"\n🏆 Top Companies (Active Jobs):")
                print("-" * 80)
                
                top_companies = db.query(
                    Job.company,
                    func.count(Job.id).label('count')
                ).filter(
                    Job.is_active == True
                ).group_by(
                    Job.company
                ).order_by(
                    func.count(Job.id).desc()
                ).limit(15).all()
                
                for company, count in top_companies:
                    print(f"  • {company}: {count} jobs")
        
        except Exception as e:
            print(f"❌ Error fetching statistics: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_export_files(self):
        """View recent export files."""
        print("\n📁 Recent Export Files")
        print("=" * 80)
        
        if not self.exports_dir.exists():
            print("No exports directory found.")
            input("\nPress Enter to continue...")
            return
        
        # Get all export files sorted by modification time
        files = sorted(
            self.exports_dir.glob("*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:10]
        
        if not files:
            print("No export files found.")
        else:
            print("Most recent exports:\n")
            for file in files:
                size = file.stat().st_size
                modified = datetime.fromtimestamp(file.stat().st_mtime)
                size_str = f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.1f} MB"
                
                print(f"📄 {file.name}")
                print(f"   Size: {size_str} | Modified: {modified.strftime('%Y-%m-%d %H:%M')}")
                print()
        
        input("\nPress Enter to continue...")
    
    def update_master_log(self):
        """Update master CSV log with all jobs."""
        try:
            with get_db_context() as db:
                # Get all jobs
                jobs = db.query(Job).order_by(Job.first_seen_at.desc()).all()
                
                # Write to CSV
                with open(self.master_log, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Header
                    writer.writerow([
                        'ID', 'Company', 'Title', 'Location', 'Remote',
                        'Category', 'Employment Type', 'Posted Date',
                        'First Seen', 'Last Seen', 'Is Active', 'URL', 'Tags'
                    ])
                    
                    # Data
                    for job in jobs:
                        writer.writerow([
                            job.id,
                            job.company,
                            job.title,
                            job.location or '',
                            'Yes' if job.remote else 'No',
                            job.category or '',
                            job.employment_type or '',
                            job.posted_at.strftime('%Y-%m-%d') if job.posted_at else '',
                            job.first_seen_at.strftime('%Y-%m-%d %H:%M') if job.first_seen_at else '',
                            job.last_seen_at.strftime('%Y-%m-%d %H:%M') if job.last_seen_at else '',
                            'Yes' if job.is_active else 'No',
                            job.url,
                            ','.join(job.tags) if job.tags else ''
                        ])
                
                print(f"\n  \033[1;32m✅ Master log updated: {self.master_log}\033[0m")
                print(f"  \033[1;36m   Total jobs: {len(jobs)}\033[0m")
        
        except Exception as e:
            print(f"\n  \033[1;33m⚠️  Could not update master log: Database connection unavailable\033[0m")
            print(f"  \033[0;90m   (The scrape completed successfully, but CSV export requires database access)\033[0m")
            print(f"  \033[1;36m   💡 Tip: Export the master log using Option 7 when database is running\033[0m")
    
    def export_master_log(self):
        """Export master job log with timestamp."""
        print("\n\033[1;34m")  # Blue
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                      💾  EXPORT MASTER JOB LOG (CSV)                          ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print("\n  \033[1;33m⏳ Connecting to database and generating CSV...\033[0m\n")
        
        self.update_master_log()
        
        # Create timestamped copy
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = self.exports_dir / f"master_log_{timestamp}.csv"
        
        # Only create timestamped copy if master log was successfully created
        if self.master_log.exists():
            try:
                import shutil
                shutil.copy(self.master_log, export_file)
                print(f"\n  \033[1;32m✅ Timestamped copy saved:\033[0m")
                print(f"     \033[1;36m{export_file}\033[0m")
                print(f"\n  \033[1;32m📍 Main log location:\033[0m")
                print(f"     \033[1;36m{self.master_log}\033[0m")
                print(f"\n  \033[1;33m💡 Open in Excel/Sheets for best experience\033[0m")
            
            except Exception as e:
                print(f"\n  \033[1;31m❌ Error creating copy: {e}\033[0m")
        
        input("\n  \033[1;32m✓\033[0m Press Enter to continue...")
    
    def search_jobs(self):
        """Search jobs by keyword."""
        print("\n🔍 Search Jobs")
        print("=" * 80)
        
        keyword = input("Enter search keyword (title/company/location): ").strip()
        if not keyword:
            print("❌ No keyword provided.")
            input("\nPress Enter to continue...")
            return
        
        try:
            with get_db_context() as db:
                # Search in title, company, location
                jobs = db.query(Job).filter(
                    and_(
                        Job.is_active == True,
                        (
                            Job.title.ilike(f'%{keyword}%') |
                            Job.company.ilike(f'%{keyword}%') |
                            Job.location.ilike(f'%{keyword}%')
                        )
                    )
                ).order_by(Job.first_seen_at.desc()).limit(50).all()
                
                if not jobs:
                    print(f"\nNo jobs found matching '{keyword}'")
                else:
                    print(f"\nFound {len(jobs)} jobs matching '{keyword}':\n")
                    
                    for job in jobs:
                        print(f"🏢 {job.company}")
                        print(f"📋 {job.title}")
                        print(f"📍 {job.location or 'Remote'}")
                        print(f"🔗 {job.url}")
                        if job.category:
                            print(f"🏷️  {job.category}")
                        print("-" * 80)
        
        except Exception as e:
            print(f"❌ Error searching jobs: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_jobs_by_company(self):
        """View jobs for a specific company."""
        print("\n🏢 View Jobs by Company")
        print("=" * 80)
        
        company = input("Enter company name: ").strip()
        if not company:
            print("❌ No company name provided.")
            input("\nPress Enter to continue...")
            return
        
        try:
            with get_db_context() as db:
                jobs = db.query(Job).filter(
                    and_(
                        Job.is_active == True,
                        Job.company.ilike(f'%{company}%')
                    )
                ).order_by(Job.first_seen_at.desc()).all()
                
                if not jobs:
                    print(f"\nNo active jobs found for '{company}'")
                else:
                    # Group by company name (in case of partial matches)
                    companies = {}
                    for job in jobs:
                        if job.company not in companies:
                            companies[job.company] = []
                        companies[job.company].append(job)
                    
                    for comp_name, comp_jobs in companies.items():
                        print(f"\n🏢 {comp_name} ({len(comp_jobs)} jobs)")
                        print("=" * 80)
                        
                        for job in comp_jobs:
                            print(f"\n📋 {job.title}")
                            print(f"📍 {job.location or 'Remote'}")
                            print(f"📅 First Seen: {job.first_seen_at.strftime('%Y-%m-%d')}")
                            if job.category:
                                print(f"🏷️  {job.category}")
                            print(f"🔗 {job.url}")
                            print("-" * 40)
        
        except Exception as e:
            print(f"❌ Error fetching jobs: {e}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the interactive CLI."""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            choice = input("\n👉 Select an option (0-9): ").strip()
            
            if choice == '1':
                self.run_full_scrape()
            elif choice == '2':
                self.run_single_scrape()
            elif choice == '3':
                self.view_today_stats()
            elif choice == '4':
                self.view_new_jobs()
            elif choice == '5':
                self.view_all_time_stats()
            elif choice == '6':
                self.view_export_files()
            elif choice == '7':
                self.export_master_log()
            elif choice == '8':
                self.search_jobs()
            elif choice == '9':
                self.view_jobs_by_company()
            elif choice == '0':
                self.clear_screen()
                print("\n\033[1;36m")
                print("╔════════════════════════════════════════════════════════════════════════════════╗")
                print("║                                                                                ║")
                print("║                           👋  THANKS FOR USING                                 ║")
                print("║                              JOB TRACKER!                                      ║")
                print("║                                                                                ║")
                print("║                     🎯 Good luck with your internship search! 🎯              ║")
                print("║                                                                                ║")
                print("╚════════════════════════════════════════════════════════════════════════════════╝")
                print("\033[0m\n")
                break
            else:
                print("\n  \033[1;31m❌ Invalid option. Please select 0-9.\033[0m")
                input("\n  Press Enter to continue...")


def main():
    """Entry point."""
    cli = JobTrackerCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
