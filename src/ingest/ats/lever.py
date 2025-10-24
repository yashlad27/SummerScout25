"""Lever ATS scraper."""

from datetime import datetime
from typing import Any

from src.ingest.base import BaseScraper
from src.ingest.schemas import RawJob, WatchlistTarget
from src.utils.http import get_with_retry
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class LeverScraper(BaseScraper):
    """Scraper for Lever job boards."""
    
    source = "lever"
    
    def __init__(self, target: WatchlistTarget):
        super().__init__(target)
        self.company_slug = self._extract_slug()
    
    def _extract_slug(self) -> str:
        """Extract company slug from careers URL or company name."""
        if self.target.careers_url and "lever.co" in self.target.careers_url:
            # Extract from URL like https://jobs.lever.co/twosigma
            parts = self.target.careers_url.rstrip("/").split("/")
            return parts[-1]
        
        # Use company name
        return self.company.lower().replace(" ", "").replace(".", "")
    
    def fetch(self) -> list[RawJob]:
        """Fetch jobs from Lever.
        
        Returns:
            List of raw jobs
        """
        jobs: list[RawJob] = []
        
        try:
            # Lever API endpoint
            url = f"https://api.lever.co/v0/postings/{self.company_slug}"
            
            self.logger.info(f"Fetching Lever jobs for {self.company} from {url}")
            
            params = {"mode": "json"}
            response = get_with_retry(url, params=params)
            job_listings = response.json()
            
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
            self.logger.error(f"Failed to fetch Lever jobs for {self.company}: {e}")
            return []
    
    def _parse_job(self, job_data: dict[str, Any]) -> RawJob:
        """Parse a single Lever job.
        
        Args:
            job_data: Raw job data from API
            
        Returns:
            RawJob instance
        """
        job_id = job_data["id"]
        title = job_data["text"]
        
        # Location
        categories = job_data.get("categories", {})
        location_str = categories.get("location")
        
        # URL
        url = job_data.get("hostedUrl", "")
        
        # Posted date
        posted_at = None
        if "createdAt" in job_data:
            try:
                # Lever uses milliseconds timestamp
                timestamp_ms = job_data["createdAt"]
                posted_at = datetime.fromtimestamp(timestamp_ms / 1000)
            except Exception:
                pass
        
        # Description - combine lists
        description_parts = []
        lists = job_data.get("lists", [])
        for list_item in lists:
            content = list_item.get("content", "")
            if content:
                description_parts.append(content)
        
        description_html = "<br/>".join(description_parts) if description_parts else job_data.get("description", "")
        
        # Determine if remote
        remote = False
        if location_str:
            remote = "remote" in location_str.lower()
        
        return self._create_raw_job(
            source_id=job_id,
            title=title,
            location=location_str,
            url=url,
            posted_at=posted_at,
            description_html=description_html,
            remote=remote,
            raw_data=job_data,
        )
