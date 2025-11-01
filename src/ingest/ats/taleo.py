"""Taleo ATS scraper - used by Oracle and many large enterprises."""

import requests
from bs4 import BeautifulSoup
from typing import List
from src.ingest.schemas import JobPosting
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class TaleoScraper:
    """Scraper for Taleo ATS job boards."""
    
    def __init__(self, company: str, taleo_url: str):
        """
        Initialize Taleo scraper.
        
        Args:
            company: Company name
            taleo_url: Full Taleo careers URL
        """
        self.company = company
        self.base_url = taleo_url
        self.logger = logger
    
    def fetch(self) -> List[JobPosting]:
        """
        Fetch jobs from Taleo portal.
        
        Returns:
            List of JobPosting objects
        """
        jobs = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            self.logger.info(f"Fetching Taleo jobs for {self.company}")
            
            response = requests.get(
                self.base_url,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Taleo has various formats - try common selectors
                job_rows = soup.select('.requisitionListResultsRow, .job-listing, .job-row, tr[id*="job"]')
                
                for row in job_rows:
                    try:
                        # Try multiple patterns for title and link
                        title_elem = row.select_one('.jobTitle, .job-title, a[title]')
                        location_elem = row.select_one('.jobLocation, .job-location, .location')
                        link_elem = row.select_one('a[href*="jobdetail"], a[href*="job"], a[title]')
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        title = title_elem.get('title') or title_elem.get_text(strip=True)
                        location = location_elem.get_text(strip=True) if location_elem else ""
                        job_url = link_elem['href']
                        
                        # Make URL absolute if needed
                        if not job_url.startswith('http'):
                            base_domain = '/'.join(self.base_url.split('/')[:3])
                            if job_url.startswith('/'):
                                job_url = base_domain + job_url
                            else:
                                job_url = self.base_url.rsplit('/', 1)[0] + '/' + job_url
                        
                        # Extract job ID
                        job_id = job_url.split('=')[-1].split('&')[0]
                        
                        # Filter for internships
                        if 'intern' not in title.lower():
                            continue
                        
                        job = JobPosting(
                            source="taleo",
                            source_id=f"taleo_{job_id}",
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
                        self.logger.debug(f"Error parsing Taleo job: {e}")
                        continue
                
                self.logger.info(f"Found {len(jobs)} Taleo jobs for {self.company}")
            else:
                self.logger.error(f"Taleo returned {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"Error fetching Taleo jobs: {e}")
        
        return jobs
