"""Deduplication and change detection."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.models import Job, JobVersion
from src.ingest.schemas import NormalizedJob
from src.utils.hashing import jaccard_similarity, tokenize_title
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class JobDeduper:
    """Handle job deduplication and change detection."""
    
    def __init__(self, db: Session):
        """Initialize deduper.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def process_job(self, job: NormalizedJob) -> tuple[Job, bool]:
        """Process a job for deduplication and change detection.
        
        Args:
            job: Normalized job
            
        Returns:
            Tuple of (Job model, is_new)
        """
        # Check if job exists by source + source_id
        existing = self.db.query(Job).filter(
            Job.source == job.source,
            Job.source_id == job.source_id,
        ).first()
        
        if existing:
            return self._update_existing(existing, job), False
        else:
            return self._create_new(job), True
    
    def _create_new(self, job: NormalizedJob) -> Job:
        """Create a new job record.
        
        Args:
            job: Normalized job
            
        Returns:
            New Job model
        """
        now = datetime.utcnow()
        
        db_job = Job(
            source=job.source,
            source_id=job.source_id,
            company=job.company,
            title=job.title,
            location=job.location,
            remote=job.remote,
            employment_type=job.employment_type,
            posted_at=job.posted_at,
            url=job.url,
            description_md=job.description_md,
            hash_stable=job.hash_stable,
            hash_full=job.hash_full,
            first_seen_at=now,
            last_seen_at=now,
            is_active=True,
            category=job.category,
            tags=job.tags,
            raw_data=job.raw_data,
        )
        
        self.db.add(db_job)
        logger.info(f"Created new job: {job.company} - {job.title}")
        
        return db_job
    
    def _update_existing(self, existing: Job, job: NormalizedJob) -> Job:
        """Update an existing job if changed.
        
        Args:
            existing: Existing Job model
            job: Normalized job
            
        Returns:
            Updated Job model
        """
        # Update last_seen_at
        existing.last_seen_at = datetime.utcnow()
        existing.is_active = True
        
        # Check if content changed
        if existing.hash_full != job.hash_full:
            logger.info(f"Job changed: {job.company} - {job.title}")
            
            # Create version record
            self._create_version(existing, job)
            
            # Update fields
            existing.title = job.title
            existing.location = job.location
            existing.remote = job.remote
            existing.employment_type = job.employment_type
            existing.posted_at = job.posted_at
            existing.url = job.url
            existing.description_md = job.description_md
            existing.hash_full = job.hash_full
            existing.category = job.category
            existing.tags = job.tags
            existing.raw_data = job.raw_data
        else:
            logger.debug(f"Job unchanged: {job.company} - {job.title}")
        
        return existing
    
    def _create_version(self, existing: Job, new_job: NormalizedJob) -> None:
        """Create a version record for a changed job.
        
        Args:
            existing: Existing Job model
            new_job: New normalized job data
        """
        # Compute diff (simple field comparison)
        diff = {}
        
        if existing.title != new_job.title:
            diff["title"] = {"old": existing.title, "new": new_job.title}
        
        if existing.location != new_job.location:
            diff["location"] = {"old": existing.location, "new": new_job.location}
        
        if existing.employment_type != new_job.employment_type:
            diff["employment_type"] = {"old": existing.employment_type, "new": new_job.employment_type}
        
        # Create version record
        version = JobVersion(
            job_id=existing.id,
            hash_full=new_job.hash_full,
            captured_at=datetime.utcnow(),
            diff_json=diff,
            snapshot={
                "title": new_job.title,
                "location": new_job.location,
                "employment_type": new_job.employment_type,
                "posted_at": new_job.posted_at.isoformat() if new_job.posted_at else None,
                "url": new_job.url,
            },
        )
        
        self.db.add(version)
        logger.debug(f"Created version for job {existing.id}: {diff}")
    
    def find_cross_source_duplicates(
        self,
        job: NormalizedJob,
        threshold: float = 0.8,
    ) -> list[Job]:
        """Find potential duplicates from other sources.
        
        Args:
            job: Normalized job
            threshold: Jaccard similarity threshold
            
        Returns:
            List of potential duplicate jobs
        """
        # Get jobs from same company with different source
        candidates = self.db.query(Job).filter(
            Job.company == job.company,
            Job.source != job.source,
            Job.is_active == True,
        ).all()
        
        duplicates = []
        job_tokens = tokenize_title(job.title)
        
        for candidate in candidates:
            candidate_tokens = tokenize_title(candidate.title)
            similarity = jaccard_similarity(job_tokens, candidate_tokens)
            
            # Also check location match
            location_match = (
                job.location == candidate.location
                or (job.remote and candidate.remote)
            )
            
            if similarity >= threshold and location_match:
                duplicates.append(candidate)
                logger.info(
                    f"Found cross-source duplicate: "
                    f"{job.source}/{job.source_id} <-> {candidate.source}/{candidate.source_id} "
                    f"(similarity: {similarity:.2f})"
                )
        
        return duplicates
    
    def mark_inactive(self, job_ids: list[str]) -> int:
        """Mark jobs as inactive.
        
        Args:
            job_ids: List of job IDs to mark inactive
            
        Returns:
            Number of jobs marked inactive
        """
        count = self.db.query(Job).filter(
            Job.id.in_(job_ids)
        ).update(
            {"is_active": False},
            synchronize_session=False,
        )
        
        logger.info(f"Marked {count} jobs as inactive")
        return count
