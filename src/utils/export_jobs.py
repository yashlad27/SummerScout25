"""Export jobs to txt and xlsx files."""

import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

from src.core.models import Job
from src.core.config import get_settings

settings = get_settings()


def export_jobs_to_files(country: str = "us"):
    """Export jobs to .txt and .xlsx files.
    
    Args:
        country: Country filter (us or india)
    """
    # Create exports directory
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    # Connect to database
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query active jobs for the country
        jobs = session.query(Job).filter(
            Job.is_active == True,
            Job.country == country
        ).order_by(Job.company, Job.title).all()
        
        if not jobs:
            print(f"No jobs found for {country}")
            return
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        country_label = country.upper()
        
        # Export to TXT
        txt_file = export_dir / f"jobs_{country}_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"  {country_label} INTERNSHIPS - Summer 2026\n")
            f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Total Jobs: {len(jobs)}\n")
            f.write(f"{'='*80}\n\n")
            
            current_company = None
            for job in jobs:
                # Company header
                if job.company != current_company:
                    if current_company:
                        f.write("\n")
                    f.write(f"\n{'─'*80}\n")
                    f.write(f"🏢 {job.company}\n")
                    f.write(f"{'─'*80}\n\n")
                    current_company = job.company
                
                # Job details
                f.write(f"📋 {job.title}\n")
                if job.location:
                    f.write(f"📍 Location: {job.location}\n")
                if job.category:
                    f.write(f"🏷️  Category: {job.category}\n")
                if job.remote:
                    f.write(f"🏠 Remote: Yes\n")
                f.write(f"🔗 URL: {job.url}\n")
                f.write(f"📅 First Seen: {job.first_seen_at.strftime('%Y-%m-%d')}\n")
                f.write(f"\n")
        
        print(f"✅ Exported to: {txt_file}")
        
        # Export to XLSX
        xlsx_file = export_dir / f"jobs_{country}_{timestamp}.xlsx"
        
        # Prepare data for DataFrame
        data = []
        for job in jobs:
            data.append({
                'Company': job.company,
                'Title': job.title,
                'Location': job.location or 'Not specified',
                'Category': job.category or 'Uncategorized',
                'Remote': 'Yes' if job.remote else 'No',
                'URL': job.url,
                'First Seen': job.first_seen_at.strftime('%Y-%m-%d'),
                'Last Updated': job.last_seen_at.strftime('%Y-%m-%d'),
            })
        
        # Create DataFrame and export
        df = pd.DataFrame(data)
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Internships')
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Internships']
            
            # Adjust column widths
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length, 50)
            
            # Format header row
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
        
        print(f"✅ Exported to: {xlsx_file}")
        
        # Also create a summary file
        summary_file = export_dir / f"summary_{country}_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"{country_label} Internships Summary\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Total Jobs: {len(jobs)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Jobs by company
            f.write(f"Jobs by Company:\n")
            f.write(f"{'-'*60}\n")
            company_counts = {}
            for job in jobs:
                company_counts[job.company] = company_counts.get(job.company, 0) + 1
            
            for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {company:.<40} {count:>3} jobs\n")
            
            f.write(f"\n")
            
            # Jobs by category
            f.write(f"Jobs by Category:\n")
            f.write(f"{'-'*60}\n")
            category_counts = {}
            for job in jobs:
                cat = job.category or 'Uncategorized'
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {category:.<40} {count:>3} jobs\n")
        
        print(f"✅ Summary saved to: {summary_file}")
        print(f"\n📊 Exported {len(jobs)} jobs to exports/ folder")
        
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    country = sys.argv[1] if len(sys.argv) > 1 else "us"
    export_jobs_to_files(country)
