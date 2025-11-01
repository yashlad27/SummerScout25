"""Workday ATS scraper - handles 40% of Fortune 500 companies."""

import requests
from typing import List
from src.ingest.base import BaseScraper
from src.ingest.schemas import RawJob, WatchlistTarget
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class WorkdayScraper(BaseScraper):
    """Scraper for Workday ATS job boards."""
    
    source = "workday"
    
    def __init__(self, target: WatchlistTarget):
        """
        Initialize Workday scraper.
        
        Args:
            target: Watchlist target configuration
        """
        super().__init__(target)
        self.workday_company_id = getattr(target, 'workday_company_id', target.company.lower().replace(' ', ''))
        # Workday API endpoint pattern
        self.base_url = f"https://{self.workday_company_id}.wd1.myworkdayjobs.com/wday/cxs/{self.workday_company_id}/External/jobs"
    
    def fetch(self) -> List[RawJob]:
        """
        Fetch jobs from Workday API.
        
        Returns:
            List of RawJob objects
        """
        jobs = []
        
        try:
            # Workday uses a specific API format
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            # Workday API payload for searching internships
            payload = {
                "appliedFacets": {},
                "limit": 20,
                "offset": 0,
                "searchText": "intern software engineer"
            }
            
            self.logger.info(f"Fetching Workday jobs for {self.company} from {self.base_url}")
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                job_postings = data.get("jobPostings", [])
                
                for job_data in job_postings:
                    try:
                        title = job_data.get("title", "")
                        job_id = job_data.get("bulletFields", [{}])[0].get("value", "")
                        location = job_data.get("locationsText", "")
                        posted_on = job_data.get("postedOn", "")
                        
                        # Build job URL
                        job_req_id = job_data.get("externalPath", "")
                        job_url = f"https://{self.workday_company_id}.wd1.myworkdayjobs.com{job_req_id}"
                        
                        job = self._create_raw_job(
                            source_id=job_id or job_req_id,
                            title=title,
                            location=location,
                            url=job_url,
                            posted_at=posted_on,
                            description_html=f"<h1>{title}</h1><p><strong>Company:</strong> {self.company}</p><p><strong>Location:</strong> {location}</p>",
                            raw_data=job_data
                        )
                        
                        jobs.append(job)
                    
                    except Exception as e:
                        self.logger.error(f"Error parsing Workday job: {e}")
                        continue
                
                self.logger.info(f"Found {len(jobs)} jobs for {self.company}")
            else:
                self.logger.error(f"Workday API returned {response.status_code}")
        
        except requests.Timeout:
            self.logger.error(f"Timeout fetching from {self.base_url}")
        except Exception as e:
            self.logger.error(f"Error fetching Workday jobs: {e}")
        
        return jobs
