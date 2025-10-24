"""Scraper registry for ATS types."""

from typing import Type

from src.ingest.base import BaseScraper
from src.ingest.ats.greenhouse import GreenhouseScraper
from src.ingest.ats.lever import LeverScraper
from src.ingest.ats.ashby import AshbyScraper
from src.ingest.ats.indeed import IndeedScraper, LinkedInScraper, GlassdoorScraper
from src.ingest.ats.generic import GenericScraper
from src.ingest.schemas import WatchlistTarget
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


# Registry mapping ATS type to scraper class
SCRAPER_REGISTRY: dict[str, Type[BaseScraper]] = {
    "greenhouse": GreenhouseScraper,
    "lever": LeverScraper,
    "ashby": AshbyScraper,
    "generic": GenericScraper,  # Generic web scraper using Playwright
    "indeed": IndeedScraper,
    "linkedin": LinkedInScraper,  # NOT RECOMMENDED - see warnings
    "glassdoor": GlassdoorScraper,  # NOT RECOMMENDED - see warnings
    # Add more scrapers as implemented
    # "smartrecruiters": SmartRecruitersScraper,
    # "workday": WorkdayScraper,
}


def get_scraper(target: WatchlistTarget) -> BaseScraper | None:
    """Get scraper instance for a watchlist target.
    
    Args:
        target: Watchlist target configuration
        
    Returns:
        Scraper instance or None if not supported
    """
    ats_type = target.ats_type.lower()
    
    scraper_class = SCRAPER_REGISTRY.get(ats_type)
    
    if scraper_class is None:
        logger.warning(f"No scraper found for ATS type: {ats_type}")
        return None
    
    return scraper_class(target)


def list_supported_ats() -> list[str]:
    """Get list of supported ATS types.
    
    Returns:
        List of supported ATS type names
    """
    return list(SCRAPER_REGISTRY.keys())
