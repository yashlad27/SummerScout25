"""LinkedIn scraper - fallback when company career pages fail."""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import List
import time
import random
from src.ingest.schemas import JobPosting
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class LinkedInScraper:
    """Scraper for LinkedIn job listings as fallback source."""
    
    def __init__(self, company: str, linkedin_company_id: str = None):
        """
        Initialize LinkedIn scraper.
        
        Args:
            company: Company name
            linkedin_company_id: LinkedIn company ID (optional, will search by name)
        """
        self.company = company
        self.linkedin_company_id = linkedin_company_id
        self.logger = logger
        
        # Build search URL
        if linkedin_company_id:
            self.base_url = f"https://www.linkedin.com/jobs/search/?f_C={linkedin_company_id}&keywords=software%20engineer%20intern"
        else:
            # Search by company name
            company_encoded = company.replace(" ", "%20")
            self.base_url = f"https://www.linkedin.com/jobs/search/?keywords={company_encoded}%20software%20engineer%20intern"
    
    def fetch(self) -> List[JobPosting]:
        """
        Fetch jobs from LinkedIn.
        
        Returns:
            List of JobPosting objects
        """
        jobs = []
        
        try:
            self.logger.info(f"Fetching LinkedIn jobs for {self.company}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set realistic user agent
                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                
                # Navigate to LinkedIn jobs
                page.goto(self.base_url, wait_until="networkidle", timeout=60000)
                
                # Wait for jobs to load
                time.sleep(2 + random.random() * 2)  # Random delay to avoid detection
                
                # Scroll to load more jobs
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                
                # Extract job cards
                job_cards = page.query_selector_all(".job-search-card")
                
                for card in job_cards[:20]:  # Limit to 20 jobs
                    try:
                        # Extract job details
                        title_elem = card.query_selector(".job-search-card__title")
                        company_elem = card.query_selector(".job-search-card__company-name")
                        location_elem = card.query_selector(".job-search-card__location")
                        link_elem = card.query_selector("a.job-search-card__link-wrapper")
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        title = title_elem.inner_text().strip()
                        company_name = company_elem.inner_text().strip() if company_elem else self.company
                        location = location_elem.inner_text().strip() if location_elem else ""
                        job_url = link_elem.get_attribute("href")
                        
                        # Extract job ID from URL
                        job_id = job_url.split("/")[-1].split("?")[0] if job_url else ""
                        
                        # Filter to only include our target company
                        if self.company.lower() not in company_name.lower():
                            continue
                        
                        job = JobPosting(
                            source="linkedin",
                            source_id=f"linkedin_{job_id}",
                            company=self.company,
                            title=title,
                            location=location,
                            url=job_url,
                            description_md=f"# {title}\n\n**Company:** {company_name}\n**Location:** {location}\n\n*Source: LinkedIn*",
                            raw_data={
                                "title": title,
                                "company": company_name,
                                "location": location,
                                "url": job_url
                            }
                        )
                        
                        jobs.append(job)
                    
                    except Exception as e:
                        self.logger.debug(f"Error parsing LinkedIn job card: {e}")
                        continue
                
                browser.close()
                
                self.logger.info(f"Found {len(jobs)} LinkedIn jobs for {self.company}")
        
        except PlaywrightTimeout:
            self.logger.error(f"Timeout fetching LinkedIn jobs for {self.company}")
        except Exception as e:
            self.logger.error(f"Error fetching LinkedIn jobs: {e}")
        
        return jobs
