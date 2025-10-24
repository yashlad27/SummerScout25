#!/usr/bin/env python3
"""
Export tracked jobs to text/CSV files for easy application.
"""

import csv
from datetime import datetime
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import Session
from src.core.models import Job
from src.core.config import get_settings

settings = get_settings()

def export_to_csv(filename: str = "jobs_export.csv"):
    """Export jobs to CSV file."""
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        # Get all active jobs, most recent first
        stmt = select(Job).where(Job.is_active == True).order_by(desc(Job.first_seen_at))
        jobs = session.execute(stmt).scalars().all()
        
        print(f"Found {len(jobs)} active jobs")
        
        # Export to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Company', 'Job Title', 'Location', 'Remote', 
                'Employment Type', 'Category', 'Posted Date',
                'First Seen', 'Tags', 'Application URL'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for job in jobs:
                writer.writerow({
                    'Company': job.company,
                    'Job Title': job.title,
                    'Location': job.location or 'Not specified',
                    'Remote': 'Yes' if job.remote else 'No',
                    'Employment Type': job.employment_type or 'Internship',
                    'Category': job.category or 'N/A',
                    'Posted Date': job.posted_at.strftime('%Y-%m-%d') if job.posted_at else 'N/A',
                    'First Seen': job.first_seen_at.strftime('%Y-%m-%d %H:%M') if job.first_seen_at else 'N/A',
                    'Tags': ', '.join(job.tags) if job.tags else '',
                    'Application URL': job.url
                })
        
        print(f"✅ Exported to {filename}")
        return len(jobs)


def export_to_formatted_text(filename: str = "jobs_formatted.txt"):
    """Export jobs to nicely formatted text file."""
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        # Get all active jobs, most recent first
        stmt = select(Job).where(Job.is_active == True).order_by(desc(Job.first_seen_at))
        jobs = session.execute(stmt).scalars().all()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("SUMMER 2026 INTERNSHIP TRACKER\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Jobs: {len(jobs)}\n")
            f.write("="*80 + "\n\n")
            
            # Group by company
            jobs_by_company = {}
            for job in jobs:
                if job.company not in jobs_by_company:
                    jobs_by_company[job.company] = []
                jobs_by_company[job.company].append(job)
            
            # Write by company
            for company, company_jobs in sorted(jobs_by_company.items()):
                f.write(f"\n{'='*80}\n")
                f.write(f"🏢 {company} ({len(company_jobs)} positions)\n")
                f.write(f"{'='*80}\n\n")
                
                for idx, job in enumerate(company_jobs, 1):
                    f.write(f"  [{idx}] {job.title}\n")
                    f.write(f"      📍 Location: {job.location or 'Not specified'}\n")
                    if job.remote:
                        f.write(f"      🏠 Remote: Yes\n")
                    if job.category:
                        f.write(f"      🏷️  Category: {job.category}\n")
                    if job.tags:
                        f.write(f"      🔖 Tags: {', '.join(job.tags)}\n")
                    if job.posted_at:
                        f.write(f"      📅 Posted: {job.posted_at.strftime('%Y-%m-%d')}\n")
                    f.write(f"      🔗 Apply: {job.url}\n")
                    f.write(f"\n")
        
        print(f"✅ Exported to {filename}")
        return len(jobs)


def export_by_category(base_filename: str = "jobs_by_category"):
    """Export jobs grouped by category to separate files."""
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        stmt = select(Job).where(Job.is_active == True).order_by(desc(Job.first_seen_at))
        jobs = session.execute(stmt).scalars().all()
        
        # Group by category
        jobs_by_category = {}
        for job in jobs:
            category = job.category or 'uncategorized'
            if category not in jobs_by_category:
                jobs_by_category[category] = []
            jobs_by_category[category].append(job)
        
        # Export each category
        for category, category_jobs in jobs_by_category.items():
            filename = f"{base_filename}_{category}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"{'='*80}\n")
                f.write(f"CATEGORY: {category.upper()}\n")
                f.write(f"Total Jobs: {len(category_jobs)}\n")
                f.write(f"{'='*80}\n\n")
                
                for job in category_jobs:
                    f.write(f"🏢 {job.company}\n")
                    f.write(f"💼 {job.title}\n")
                    f.write(f"📍 {job.location or 'Not specified'}\n")
                    if job.remote:
                        f.write(f"🏠 Remote: Yes\n")
                    if job.posted_at:
                        f.write(f"📅 Posted: {job.posted_at.strftime('%Y-%m-%d')}\n")
                    f.write(f"🔗 {job.url}\n")
                    f.write(f"\n{'-'*80}\n\n")
            
            print(f"✅ Exported {len(category_jobs)} jobs to {filename}")
        
        return len(jobs)


def main():
    """Export jobs in all formats."""
    print("\n" + "="*80)
    print("JOB EXPORT TOOL")
    print("="*80 + "\n")
    
    try:
        # Export to CSV
        print("📊 Exporting to CSV...")
        csv_count = export_to_csv("jobs_export.csv")
        
        # Export to formatted text
        print("\n📝 Exporting to formatted text...")
        txt_count = export_to_formatted_text("jobs_formatted.txt")
        
        # Export by category
        print("\n📁 Exporting by category...")
        cat_count = export_by_category("jobs_by_category")
        
        print("\n" + "="*80)
        print("✅ EXPORT COMPLETE!")
        print("="*80)
        print(f"\nFiles created:")
        print(f"  📄 jobs_export.csv - Spreadsheet format ({csv_count} jobs)")
        print(f"  📄 jobs_formatted.txt - Readable text format ({txt_count} jobs)")
        print(f"  📁 jobs_by_category_*.txt - Separate files per category")
        print(f"\nYou can now:")
        print(f"  • Open jobs_export.csv in Excel/Google Sheets")
        print(f"  • Read jobs_formatted.txt for quick browsing")
        print(f"  • Click links to apply directly!")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure Docker is running and database is accessible.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
