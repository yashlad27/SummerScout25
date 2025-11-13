"""Job data normalization."""

from datetime import datetime

from src.ingest.schemas import RawJob, NormalizedJob
from src.utils.hashing import (
    compute_hash_stable,
    compute_hash_full,
    compute_description_digest,
)
from src.utils.text import html_to_markdown, is_remote_location
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class JobNormalizer:
    """Normalize raw jobs to standardized schema."""
    
    def normalize(self, raw_job: RawJob) -> NormalizedJob:
        """Normalize a raw job to the standard format.
        
        Args:
            raw_job: Raw job data from scraper
            
        Returns:
            Normalized job
        """
        # Convert HTML description to Markdown
        description_md = ""
        if raw_job.description_html:
            description_md = html_to_markdown(raw_job.description_html)
        elif raw_job.description_md:
            description_md = raw_job.description_md
        
        # Compute hashes
        hash_stable = compute_hash_stable(
            title=raw_job.title,
            company=raw_job.company,
            location=raw_job.location or "",
            url=raw_job.url,
        )
        
        description_digest = compute_description_digest(description_md)
        
        hash_full = compute_hash_full(
            hash_stable=hash_stable,
            employment_type=raw_job.employment_type,
            posted_at=raw_job.posted_at.isoformat() if raw_job.posted_at else None,
            description_digest=description_digest,
        )
        
        return NormalizedJob(
            source=raw_job.source,
            source_id=raw_job.source_id,
            company=raw_job.company,
            title=raw_job.title,
            location=raw_job.location,
            employment_type=raw_job.employment_type,
            posted_at=raw_job.posted_at,
            url=raw_job.url,
            description_md=description_md,
            hash_stable=hash_stable,
            hash_full=hash_full,
            raw_data=raw_job.raw_data,
        )
