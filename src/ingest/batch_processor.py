"""Batch processor for efficient database operations."""

from typing import List
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from src.core.models import Job
from src.ingest.schemas import NormalizedJob
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class BatchJobProcessor:
    """Process jobs in batches for better performance."""
    
    def __init__(self, db: Session, batch_size: int = 50):
        """Initialize batch processor.
        
        Args:
            db: Database session
            batch_size: Number of jobs to process per batch
        """
        self.db = db
        self.batch_size = batch_size
        self.job_buffer = []
        self.new_job_ids = []
        self.updated_job_ids = []
    
    def add_job(self, job: NormalizedJob, category: str, tags: List[str]):
        """Add a job to the batch buffer.
        
        Args:
            job: Normalized job
            category: Job category
            tags: Job tags
        """
        self.job_buffer.append({
            'job': job,
            'category': category,
            'tags': tags
        })
        
        # Flush if buffer is full
        if len(self.job_buffer) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Process all buffered jobs."""
        if not self.job_buffer:
            return
        
        logger.debug(f"Processing batch of {len(self.job_buffer)} jobs")
        
        # Separate new and existing jobs
        source_ids = [(item['job'].source, item['job'].source_id) for item in self.job_buffer]
        
        # Query existing jobs in one go
        existing_jobs = {}
        if source_ids:
            # Build query for all source/source_id combinations
            from sqlalchemy import or_, and_
            conditions = [
                and_(Job.source == source, Job.source_id == source_id)
                for source, source_id in source_ids
            ]
            
            existing = self.db.query(Job).filter(or_(*conditions)).all()
            for job in existing:
                existing_jobs[(job.source, job.source_id)] = job
        
        # Process each job
        now = datetime.utcnow()
        new_jobs = []
        
        for item in self.job_buffer:
            job_data = item['job']
            category = item['category']
            tags = item['tags']
            
            key = (job_data.source, job_data.source_id)
            existing = existing_jobs.get(key)
            
            if existing:
                # Update existing job
                existing.last_seen_at = now
                existing.is_active = True
                
                # Check if content changed
                if existing.hash_full != job_data.hash_full:
                    existing.title = job_data.title
                    existing.location = job_data.location
                    existing.employment_type = job_data.employment_type
                    existing.posted_at = job_data.posted_at
                    existing.url = job_data.url
                    existing.description_md = job_data.description_md
                    existing.hash_full = job_data.hash_full
                    existing.category = category
                    existing.tags = tags
                    
                    self.db.flush()
                    self.updated_job_ids.append(existing.id)
            else:
                # Create new job
                new_job = Job(
                    source=job_data.source,
                    source_id=job_data.source_id,
                    company=job_data.company,
                    title=job_data.title,
                    location=job_data.location,
                    employment_type=job_data.employment_type,
                    posted_at=job_data.posted_at,
                    url=job_data.url,
                    description_md=job_data.description_md,
                    hash_stable=job_data.hash_stable,
                    hash_full=job_data.hash_full,
                    first_seen_at=now,
                    last_seen_at=now,
                    is_active=True,
                    category=category,
                    tags=tags,
                    raw_data=job_data.raw_data,
                    country=job_data.country,
                )
                new_jobs.append(new_job)
        
        # Bulk insert new jobs
        if new_jobs:
            self.db.add_all(new_jobs)
            self.db.flush()
            
            # Collect IDs
            for job in new_jobs:
                self.new_job_ids.append(job.id)
        
        logger.debug(f"Batch processed: {len(new_jobs)} new, {len(self.updated_job_ids) - len(self.new_job_ids)} updated")
        
        # Clear buffer
        self.job_buffer.clear()
    
    def get_stats(self) -> tuple[List, List]:
        """Get lists of new and updated job IDs.
        
        Returns:
            Tuple of (new job IDs, updated job IDs)
        """
        return self.new_job_ids, self.updated_job_ids
