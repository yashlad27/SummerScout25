"""iCIMS ATS scraper - used by many mid-size companies."""

import requests
from bs4 import BeautifulSoup
from typing import List
from src.ingest.base import BaseScraper
from src.ingest.schemas import RawJob, WatchlistTarget
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class iCIMSScraper(BaseScraper):
    """Scraper for iCIMS ATS job boards."""
    
    source = "icims"
    
    def __init__(self, target: WatchlistTarget):
        """
        Initialize iCIMS scraper.
        
        Args:
            target: Watchlist target configuration
        """
        super().__init__(target)
        self.icims_id = getattr(target, 'icims_id', f"careers-{target.company.lower().replace(' ', '')}")
        # iCIMS URL pattern
        self.base_url = f"https://{self.icims_id}.icims.com/jobs/search"
    
    def fetch(self) -> List[RawJob]:
        """
        Fetch jobs from iCIMS portal.
        
        Returns:
            List of RawJob objects
        """
        jobs = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            params = {
                "searchKeyword": "software engineer intern",
                "searchRelation": "keyword_all"
            }
            
            self.logger.info(f"Fetching iCIMS jobs for {self.company}")
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings (iCIMS specific selectors)
                job_rows = soup.select('.iCIMS_JobsTable .row')
                
                for row in job_rows:
                    try:
                        title_elem = row.select_one('.title')
                        location_elem = row.select_one('.location')
                        link_elem = row.select_one('a[href*="/jobs/"]')
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        location = location_elem.get_text(strip=True) if location_elem else ""
                        job_url = link_elem['href']
                        
                        # Make URL absolute if needed
                        if not job_url.startswith('http'):
                            job_url = f"https://{self.icims_id}.icims.com{job_url}"
                        
                        # Extract job ID from URL
                        job_id = job_url.split('/')[-1].split('?')[0]
                        
                        job = self._create_raw_job(
                            source_id=f"icims_{job_id}",
                            title=title,
                            location=location,
                            url=job_url,
                            description_html=f"<h1>{title}</h1><p><strong>Company:</strong> {self.company}</p><p><strong>Location:</strong> {location}</p>",
                            raw_data={
                                "title": title,
                                "location": location,
                                "url": job_url
                            }
                        )
                        
                        jobs.append(job)
                    
                    except Exception as e:
                        self.logger.debug(f"Error parsing iCIMS job: {e}")
                        continue
                
                self.logger.info(f"Found {len(jobs)} iCIMS jobs for {self.company}")
            else:
                self.logger.error(f"iCIMS returned {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"Error fetching iCIMS jobs: {e}")
        
        return jobs
