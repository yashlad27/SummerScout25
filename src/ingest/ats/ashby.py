"""Ashby ATS scraper."""

from datetime import datetime
from typing import Any

from src.ingest.base import BaseScraper
from src.ingest.schemas import RawJob, WatchlistTarget
from src.utils.http import post_with_retry
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AshbyScraper(BaseScraper):
    """Scraper for Ashby job boards."""
    
    source = "ashby"
    
    def __init__(self, target: WatchlistTarget):
        super().__init__(target)
        self.company_slug = self._extract_slug()
    
    def _extract_slug(self) -> str:
        """Extract company slug from careers URL or company name."""
        if self.target.careers_url and "ashbyhq.com" in self.target.careers_url:
            # Extract from URL like https://jobs.ashbyhq.com/company
            parts = self.target.careers_url.rstrip("/").split("/")
            return parts[-1]
        
        # Use company name
        return self.company.lower().replace(" ", "-").replace(".", "")
    
    def fetch(self) -> list[RawJob]:
        """Fetch jobs from Ashby.
        
        Returns:
            List of raw jobs
        """
        jobs: list[RawJob] = []
        
        try:
            # Ashby GraphQL-like API endpoint
            url = "https://jobs.ashbyhq.com/api/non-user-graphql"
            
            # Query payload
            query = {
                "operationName": "ApiJobBoardWithTeams",
                "variables": {
                    "organizationHostedJobsPageName": self.company_slug
                },
                "query": """
                query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
                  jobBoard: jobPostingBoard(organizationHostedJobsPageName: $organizationHostedJobsPageName) {
                    jobPostings {
                      id
                      title
                      location
                      isRemote
                      publishedDate
                      jobUrl
                      descriptionHtml
                      department { name }
                    }
                  }
                }
                """
            }
            
            self.logger.info(f"Fetching Ashby jobs for {self.company}")
            
            response = post_with_retry(url, json=query)
            data = response.json()
            
            # Extract job postings
            job_board = data.get("data", {}).get("jobBoard", {})
            job_listings = job_board.get("jobPostings", [])
            
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
            self.logger.error(f"Failed to fetch Ashby jobs for {self.company}: {e}")
            return []
    
    def _parse_job(self, job_data: dict[str, Any]) -> RawJob:
        """Parse a single Ashby job.
        
        Args:
            job_data: Raw job data from API
            
        Returns:
            RawJob instance
        """
        job_id = job_data["id"]
        title = job_data["title"]
        location_str = job_data.get("location")
        remote = job_data.get("isRemote", False)
        url = job_data.get("jobUrl", "")
        description_html = job_data.get("descriptionHtml", "")
        
        # Posted date
        posted_at = None
        if "publishedDate" in job_data and job_data["publishedDate"]:
            try:
                posted_at = datetime.fromisoformat(job_data["publishedDate"].replace("Z", "+00:00"))
            except Exception:
                pass
        
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
