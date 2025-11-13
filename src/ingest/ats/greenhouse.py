"""Greenhouse ATS scraper."""

from datetime import datetime
from typing import Any

from src.ingest.base import BaseScraper
from src.ingest.schemas import RawJob, WatchlistTarget
from src.utils.http import get_with_retry
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class GreenhouseScraper(BaseScraper):
    """Scraper for Greenhouse job boards."""
    
    source = "greenhouse"
    
    def __init__(self, target: WatchlistTarget):
        super().__init__(target)
        # Extract company slug from careers URL or use company name
        self.company_slug = self._extract_slug()
    
    def _extract_slug(self) -> str:
        """Extract company slug from careers URL or company name."""
        if self.target.careers_url and "greenhouse.io" in self.target.careers_url:
            # Extract from URL like https://boards.greenhouse.io/citadel
            parts = self.target.careers_url.rstrip("/").split("/")
            return parts[-1]
        
        # Use company name, lowercased and hyphenated
        return self.company.lower().replace(" ", "-").replace(".", "")
    
    def fetch(self) -> list[RawJob]:
        """Fetch jobs from Greenhouse.
        
        Returns:
            List of raw jobs
        """
        jobs: list[RawJob] = []
        
        try:
            # Greenhouse job board API endpoint
            url = f"https://boards-api.greenhouse.io/v1/boards/{self.company_slug}/jobs"
            
            self.logger.info(f"Fetching Greenhouse jobs for {self.company} from {url}")
            
            response = get_with_retry(url)
            data = response.json()
            
            # Extract jobs array
            job_listings = data.get("jobs", [])
            
            self.logger.info(f"Found {len(job_listings)} jobs for {self.company}")
            
            for job_data in job_listings:
                try:
                    raw_job = self._parse_job(job_data)
                    jobs.append(raw_job)
                except Exception as e:
                    self.logger.warning(f"Failed to parse job {job_data.get('id')}: {e}")
                    continue
            
            return jobs
        
        except Exception as e:
            self.logger.error(f"Failed to fetch Greenhouse jobs for {self.company}: {e}")
            return []
    
    def _parse_job(self, job_data: dict[str, Any]) -> RawJob:
        """Parse a single Greenhouse job.
        
        Args:
            job_data: Raw job data from API
            
        Returns:
            RawJob instance
        """
        job_id = str(job_data["id"])
        title = job_data["title"]
        
        # Location
        location = job_data.get("location", {})
        location_str = location.get("name") if location else None
        
        # URL
        url = job_data.get("absolute_url", "")
        
        # Posted date
        posted_at = None
        if "updated_at" in job_data:
            try:
                posted_at = datetime.fromisoformat(job_data["updated_at"].replace("Z", "+00:00"))
            except Exception:
                pass
        
        # Description
        description_html = job_data.get("content", "")
        
        return self._create_raw_job(
            source_id=job_id,
            title=title,
            location=location_str,
            url=url,
            posted_at=posted_at,
            description_html=description_html,
            raw_data=job_data,
        )
