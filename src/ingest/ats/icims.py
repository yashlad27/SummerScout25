"""iCIMS ATS scraper - used by many mid-size companies."""

import requests
from bs4 import BeautifulSoup
from typing import List
from src.ingest.schemas import JobPosting
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class iCIMSScraper:
    """Scraper for iCIMS ATS job boards."""
    
    def __init__(self, company: str, icims_id: str):
        """
        Initialize iCIMS scraper.
        
        Args:
            company: Company name
            icims_id: iCIMS portal ID (e.g., 'careers-companyname')
        """
        self.company = company
        self.icims_id = icims_id
        # iCIMS URL pattern
        self.base_url = f"https://{icims_id}.icims.com/jobs/search"
        self.logger = logger
    
    def fetch(self) -> List[JobPosting]:
        """
        Fetch jobs from iCIMS portal.
        
        Returns:
            List of JobPosting objects
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
                        
                        job = JobPosting(
                            source="icims",
                            source_id=f"icims_{job_id}",
                            company=self.company,
                            title=title,
                            location=location,
                            url=job_url,
                            description_md=f"# {title}\n\n**Company:** {self.company}\n**Location:** {location}",
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
