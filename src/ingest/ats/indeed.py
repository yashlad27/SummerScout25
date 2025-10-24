"""
Indeed job board scraper.

IMPORTANT NOTES:
- Indeed has rate limiting and anti-bot measures
- Use Indeed Publisher API for production: https://www.indeed.com/publisher
- This scraper is for educational purposes
- Add delays between requests to avoid blocking
"""

import time
from typing import Optional
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

from src.ingest.schemas import RawJob, WatchlistTarget
from src.ingest.base import BaseScraper


class IndeedScraper(BaseScraper):
    """Scraper for Indeed job listings."""
    
    source = "indeed"
    
    def __init__(self, target: WatchlistTarget):
        super().__init__(target)
        self.base_url = "https://www.indeed.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    
    def _build_search_url(self, query: str, location: str = "", start: int = 0) -> str:
        """Build Indeed search URL."""
        params = {
            "q": query,
            "l": location,
            "start": start,
            "jt": "internship",  # Job type: internship
        }
        
        query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items() if v])
        return f"{self.base_url}/jobs?{query_string}"
    
    def fetch(self) -> list[RawJob]:
        """
        Fetch jobs from Indeed.
        
        WARNING: This method may be blocked by Indeed's anti-bot measures.
        Consider using Indeed Publisher API instead.
        
        Returns:
            List of raw jobs
        """
        jobs = []
        
        # Build search queries for this company
        search_queries = [
            f"{self.company} intern summer 2026",
            f"{self.company} internship 2026",
        ]
        
        for query in search_queries:
            try:
                # Add delay to avoid rate limiting
                time.sleep(2)
                
                url = self._build_search_url(query)
                self.logger.info(f"Fetching Indeed jobs from {url}")
                
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, "html.parser")
                job_cards = soup.find_all("div", class_="job_seen_beacon")
                
                for card in job_cards:
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse job card: {e}")
                        continue
                
                self.logger.info(f"Found {len(jobs)} jobs for query: {query}")
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    self.logger.error("Rate limited by Indeed. Please wait before retrying.")
                elif e.response.status_code == 403:
                    self.logger.error("Blocked by Indeed. Consider using Indeed Publisher API.")
                else:
                    self.logger.error(f"HTTP error fetching Indeed jobs: {e}")
            except Exception as e:
                self.logger.error(f"Failed to fetch Indeed jobs for {query}: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Optional[RawJob]:
        """Parse a single Indeed job card."""
        try:
            # Extract job ID and URL
            job_link = card.find("a", class_="jcs-JobTitle")
            if not job_link:
                return None
            
            job_id = job_link.get("data-jk", "")
            job_url = f"{self.base_url}/viewjob?jk={job_id}" if job_id else None
            
            # Extract title
            title = job_link.get_text(strip=True)
            
            # Extract company
            company_elem = card.find("span", {"data-testid": "company-name"})
            company = company_elem.get_text(strip=True) if company_elem else self.company
            
            # Extract location
            location_elem = card.find("div", {"data-testid": "text-location"})
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Extract snippet/description
            snippet_elem = card.find("div", class_="job-snippet")
            description = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            # Extract posted date
            date_elem = card.find("span", class_="date")
            posted_date = date_elem.get_text(strip=True) if date_elem else ""
            
            if not title or not job_url:
                return None
            
            return RawJob(
                source="indeed",
                source_id=job_id,
                company=company,
                title=title,
                location=location,
                url=job_url,
                description_html=description,
                posted_at=None,  # Would need to parse date string
                employment_type="internship",
                remote=False,
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing job card: {e}")
            return None


class LinkedInScraper(BaseScraper):
    """
    LinkedIn scraper - NOT RECOMMENDED.
    
    WARNING:
    - LinkedIn requires authentication
    - Aggressive anti-bot measures
    - Against LinkedIn Terms of Service
    - Account may be banned
    
    Use LinkedIn's official Talent Solutions API instead.
    """
    
    source = "linkedin"
    
    def fetch(self) -> list[RawJob]:
        """
        LinkedIn scraping is NOT IMPLEMENTED due to:
        - Requires authentication
        - Against Terms of Service
        - Aggressive anti-scraping measures
        
        Recommend: Use company career pages or LinkedIn Talent Solutions API
        """
        self.logger.warning(
            f"LinkedIn scraping not implemented for {self.company}. "
            "LinkedIn requires authentication and has strict anti-scraping policies. "
            "Please use company career pages or LinkedIn's official API instead."
        )
        return []


class GlassdoorScraper(BaseScraper):
    """
    Glassdoor scraper - NOT RECOMMENDED.
    
    WARNING:
    - Glassdoor requires authentication for job search
    - Has anti-bot protection (Cloudflare, etc.)
    - Rate limiting
    
    Use company career pages instead.
    """
    
    source = "glassdoor"
    
    def fetch(self) -> list[RawJob]:
        """
        Glassdoor scraping is NOT IMPLEMENTED due to:
        - Requires authentication
        - Cloudflare protection
        - Rate limiting
        
        Recommend: Use company career pages instead
        """
        self.logger.warning(
            f"Glassdoor scraping not implemented for {self.company}. "
            "Glassdoor requires authentication and has anti-bot protection. "
            "Please use company career pages instead."
        )
        return []
