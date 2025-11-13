"""Excel export utility for job data."""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List

from src.core.database import get_db_context
from src.core.models import Job
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ExcelExporter:
    """Export jobs to Excel format."""
    
    def __init__(self, export_dir: str = "exports"):
        """Initialize exporter.
        
        Args:
            export_dir: Directory to save exports
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
    
    def export_jobs(self, jobs: List[Job] = None, filename: str = None) -> str:
        """Export jobs to Excel file.
        
        Args:
            jobs: List of Job objects. If None, exports all active jobs.
            filename: Output filename. If None, generates timestamped name.
            
        Returns:
            Path to exported file
        """
        # Query jobs if not provided
        if jobs is None:
            with get_db_context() as db:
                jobs = db.query(Job).filter(Job.is_active == True).all()
        
        if not jobs:
            logger.warning("No jobs to export")
            return None
        
        # Convert jobs to DataFrame
        job_data = []
        for job in jobs:
            job_data.append({
                "Company": job.company,
                "Title": job.title,
                "Location": job.location or "Not specified",
                "Category": job.category or "Uncategorized",
                "Employment Type": job.employment_type or "Not specified",
                "Posted Date": job.posted_at.strftime("%Y-%m-%d") if job.posted_at else "Unknown",
                "First Seen": job.first_seen_at.strftime("%Y-%m-%d %H:%M") if job.first_seen_at else "",
                "URL": job.url,
                "Source": job.source,
                "Tags": ", ".join(job.tags) if job.tags else "",
                "Visa Sponsorship": self._format_bool(job.visa_sponsorship),
                "Tech Stack (Languages)": ", ".join(job.tech_stack.get("languages", [])) if job.tech_stack else "",
                "Tech Stack (Frameworks)": ", ".join(job.tech_stack.get("frameworks", [])) if job.tech_stack else "",
                "Tech Stack (Tools)": ", ".join(job.tech_stack.get("tools", [])) if job.tech_stack else "",
                "Compensation Min": job.compensation_min,
                "Compensation Max": job.compensation_max,
                "Start Date": job.start_date or "",
                "Duration": job.duration or "",
                "Application Status": job.application_status or "Not Applied",
                "Notes": job.notes or "",
            })
        
        df = pd.DataFrame(job_data)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_export_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not filename.endswith(".xlsx"):
            filename = f"{filename}.xlsx"
        
        filepath = self.export_dir / filename
        
        # Export to Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Jobs', index=False)
            
            # Get the worksheet
            worksheet = writer.sheets['Jobs']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Max width of 50
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"✅ Exported {len(jobs)} jobs to {filepath}")
        return str(filepath)
    
    def export_by_category(self, filename: str = None) -> str:
        """Export jobs grouped by category to separate sheets.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        with get_db_context() as db:
            jobs = db.query(Job).filter(Job.is_active == True).all()
        
        if not jobs:
            logger.warning("No jobs to export")
            return None
        
        # Group by category
        jobs_by_category = {}
        for job in jobs:
            category = job.category or "Uncategorized"
            if category not in jobs_by_category:
                jobs_by_category[category] = []
            jobs_by_category[category].append(job)
        
        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_by_category_{timestamp}.xlsx"
        
        if not filename.endswith(".xlsx"):
            filename = f"{filename}.xlsx"
        
        filepath = self.export_dir / filename
        
        # Export each category to separate sheet
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for category, category_jobs in jobs_by_category.items():
                job_data = self._jobs_to_dict_list(category_jobs)
                df = pd.DataFrame(job_data)
                
                # Truncate sheet name if too long (Excel limit is 31 chars)
                sheet_name = category[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust columns
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"✅ Exported {len(jobs)} jobs across {len(jobs_by_category)} categories to {filepath}")
        return str(filepath)
    
    def _jobs_to_dict_list(self, jobs: List[Job]) -> List[dict]:
        """Convert list of Job objects to list of dictionaries.
        
        Args:
            jobs: List of Job objects
            
        Returns:
            List of dictionaries
        """
        job_data = []
        for job in jobs:
            job_data.append({
                "Company": job.company,
                "Title": job.title,
                "Location": job.location or "Not specified",
                "Category": job.category or "Uncategorized",
                "Employment Type": job.employment_type or "Not specified",
                "Posted Date": job.posted_at.strftime("%Y-%m-%d") if job.posted_at else "Unknown",
                "First Seen": job.first_seen_at.strftime("%Y-%m-%d %H:%M") if job.first_seen_at else "",
                "URL": job.url,
                "Source": job.source,
                "Tags": ", ".join(job.tags) if job.tags else "",
                "Visa Sponsorship": self._format_bool(job.visa_sponsorship),
                "Tech Stack (Languages)": ", ".join(job.tech_stack.get("languages", [])) if job.tech_stack else "",
                "Tech Stack (Frameworks)": ", ".join(job.tech_stack.get("frameworks", [])) if job.tech_stack else "",
                "Tech Stack (Tools)": ", ".join(job.tech_stack.get("tools", [])) if job.tech_stack else "",
                "Compensation Min": job.compensation_min,
                "Compensation Max": job.compensation_max,
                "Start Date": job.start_date or "",
                "Duration": job.duration or "",
                "Application Status": job.application_status or "Not Applied",
                "Notes": job.notes or "",
            })
        return job_data
    
    def _format_bool(self, value) -> str:
        """Format boolean value for Excel.
        
        Args:
            value: Boolean or None
            
        Returns:
            Formatted string
        """
        if value is None:
            return "Unknown"
        return "Yes" if value else "No"
