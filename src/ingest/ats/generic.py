"""
Generic web scraper for company career pages.
Uses Playwright for JavaScript-heavy sites.
"""

from typing import Optional
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from src.ingest.schemas import RawJob, WatchlistTarget
from src.ingest.base import BaseScraper


class GenericScraper(BaseScraper):
    """Generic scraper for company career pages using Playwright."""
    
    source = "generic"
    
    def __init__(self, target: WatchlistTarget):
        super().__init__(target)
        self.base_url = target.careers_url
    
    def fetch(self) -> list[RawJob]:
        """
        Fetch jobs from generic career page using Playwright.
        
        Returns:
            List of raw jobs
        """
        if not self.base_url:
            self.logger.warning(f"No careers URL provided for {self.company}")
            return []
        
        jobs = []
        
        try:
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set timeout and navigate (increased for heavy enterprise sites)
                page.set_default_timeout(60000)  # 60 seconds instead of 30
                page.goto(self.base_url, wait_until="networkidle")
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                
                # Get page content
                content = page.content()
                browser.close()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Try to find job listings
            job_links = self._extract_job_links(soup)
            
            for link in job_links[:50]:  # Limit to 50 jobs per page
                try:
                    job = self._create_raw_job(link)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Failed to parse job link: {e}")
                    continue
            
            self.logger.info(f"   ➜ Found {len(jobs)} jobs")
            
        except PlaywrightTimeout:
            self.logger.error(f"   ❌ Timeout (60s exceeded)")
        except Exception as e:
            # Log the specific error type for debugging
            error_msg = str(e)
            if "ERR_HTTP2_PROTOCOL_ERROR" in error_msg:
                self.logger.error(f"   ❌ HTTP2 protocol error (site blocking)")
            elif "ERR_NAME_NOT_RESOLVED" in error_msg:
                self.logger.error(f"   ❌ DNS error (invalid domain)")
            else:
                self.logger.error(f"   ❌ Error: {str(e)[:80]}")
        
        return jobs
    
    def _extract_job_links(self, soup: BeautifulSoup) -> list[dict]:
        """
        Extract job links from page.
        Looks for common patterns in career page HTML.
        """
        job_links = []
        
        # Common selectors for job listings
        selectors = [
            'a[href*="job"]',
            'a[href*="career"]',
            'a[href*="position"]',
            'a[href*="opening"]',
            '.job-listing a',
            '.job-item a',
            '.career-listing a',
            '[data-job-id]',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Filter for internship/2026 related
                if any(keyword in text.lower() for keyword in ['intern', '2026', 'graduate', 'summer']):
                    job_links.append({
                        'url': href,
                        'title': text,
                        'element': link
                    })
        
        return job_links
    
    def _create_raw_job(self, link_data: dict) -> Optional[RawJob]:
        """Create RawJob from extracted link data."""
        try:
            url = link_data['url']
            
            # Make URL absolute if needed
            if url.startswith('/'):
                from urllib.parse import urljoin
                url = urljoin(self.base_url, url)
            elif not url.startswith('http'):
                return None
            
            # Generate a source ID from URL
            source_id = re.sub(r'[^a-zA-Z0-9]', '_', url)[-100:]
            
            return RawJob(
                source="generic",
                source_id=source_id,
                company=self.company,
                title=link_data['title'],
                location=None,
                url=url,
                description_html=link_data['title'],
                posted_at=None,
                employment_type="internship",
            )
            
        except Exception as e:
            self.logger.warning(f"Error creating raw job: {e}")
            return None
