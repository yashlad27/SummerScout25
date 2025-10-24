#!/usr/bin/env python3
"""
Export tracked jobs to text/CSV files for easy application.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import Session
from src.core.models import Job
from src.core.config import get_settings

settings = get_settings()

# Output directory - use /app/exports which is mounted to local ./exports folder
OUTPUT_DIR = Path("/app/exports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def is_us_location(location: str, title: str = "") -> bool:
    """Check if location is in the United States."""
    if not location or not location.strip():
        # Check title for non-US locations
        if title:
            title_lower = title.lower()
            non_us_in_title = ['germany', 'france', 'netherlands', 'denmark', 'serbia',
                               'canada', 'india', 'china', 'japan', 'uk', 'london',
                               'paris', 'berlin', 'munich', 'amsterdam', 'toronto',
                               'bangalore', 'aarhus', 'belgrade', 'dublin', 'zurich']
            
            for country in non_us_in_title:
                if country in title_lower:
                    return False
        
        # If no location and no non-US in title, assume US
        return True
    
    location_lower = location.lower()
    
    # US indicators
    us_indicators = [
        'united states', 'usa', 'u.s.', 'us,',
        'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
        'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
        'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
        'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
        'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
        'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina',
        'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania',
        'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas',
        'utah', 'vermont', 'virginia', 'washington', 'west virginia',
        'wisconsin', 'wyoming', 'new york', 'los angeles', 'chicago', 'houston',
        'phoenix', 'philadelphia', 'san diego', 'dallas', 'san jose', 'austin',
        'san francisco', 'seattle', 'denver', 'boston', 'atlanta', 'miami',
        ', ca', ', ny', ', tx', ', fl', ', il', ', pa', ', wa', 'remote, us'
    ]
    
    # Check for US indicators
    for indicator in us_indicators:
        if indicator in location_lower:
            return True
    
    # Allow plain "remote"
    if location_lower == 'remote':
        return True
    
    # Reject known non-US locations
    non_us = ['canada', 'uk', 'germany', 'france', 'netherlands', 'india', 
              'singapore', 'australia', 'japan', 'china', 'serbia', 'denmark',
              'amsterdam', 'london', 'paris', 'berlin', 'munich', 'toronto',
              'bangalore', 'tokyo', 'aarhus', 'belgrade']
    
    for country in non_us:
        if country in location_lower:
            return False
    
    return False

def export_to_csv(filename: str = "jobs_export.csv"):
    """Export jobs to CSV file (US locations only)."""
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        # Get all active jobs, most recent first
        stmt = select(Job).where(Job.is_active == True).order_by(desc(Job.first_seen_at))
        all_jobs = session.execute(stmt).scalars().all()
        
        # Filter for US-only
        jobs = [job for job in all_jobs if is_us_location(job.location, job.title)]
        
        print(f"Found {len(jobs)} active jobs in the United States (filtered from {len(all_jobs)} total)")
        
        # Export to CSV
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
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
    """Export jobs to nicely formatted text file (US locations only)."""
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        # Get all active jobs, most recent first
        stmt = select(Job).where(Job.is_active == True).order_by(desc(Job.first_seen_at))
        all_jobs = session.execute(stmt).scalars().all()
        
        # Filter for US-only
        jobs = [job for job in all_jobs if is_us_location(job.location, job.title)]
        
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
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
    """Export jobs grouped by category to separate files (US locations only)."""
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        # Get all active jobs
        stmt = select(Job).where(Job.is_active == True).order_by(desc(Job.first_seen_at))
        all_jobs = session.execute(stmt).scalars().all()
        
        # Filter for US-only
        jobs = [job for job in all_jobs if is_us_location(job.location, job.title)]
        
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
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
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
        print(f"\n📁 Files saved to your local machine!")
        print(f"   Location: ./exports/")
        print(f"\nFiles created:")
        print(f"  📄 jobs_export.csv - Spreadsheet format ({csv_count} jobs)")
        print(f"  📄 jobs_formatted.txt - Readable text format ({txt_count} jobs)")
        print(f"  📁 jobs_by_category_*.txt - Separate files per category")
        print(f"\nOpen the exports folder:")
        print(f"  open exports/")
        print(f"\nOr view CSV directly:")
        print(f"  open exports/jobs_export.csv")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure Docker is running and database is accessible.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
