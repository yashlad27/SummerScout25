"""Scraper registry for ATS types."""

from typing import Type

from src.ingest.base import BaseScraper
from src.ingest.ats.greenhouse import GreenhouseScraper
from src.ingest.ats.lever import LeverScraper
from src.ingest.ats.ashby import AshbyScraper
from src.ingest.ats.indeed import IndeedScraper, GlassdoorScraper
from src.ingest.ats.generic import GenericScraper
from src.ingest.ats.workday import WorkdayScraper
from src.ingest.ats.linkedin import LinkedInScraper
from src.ingest.ats.icims import iCIMSScraper
from src.ingest.ats.taleo import TaleoScraper
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
    "linkedin": LinkedInScraper,  # Fallback when career pages fail
    "glassdoor": GlassdoorScraper,  # NOT RECOMMENDED - see warnings
    "workday": WorkdayScraper,  # 40% of F500 companies
    "icims": iCIMSScraper,  # Mid-size companies
    "taleo": TaleoScraper,  # Oracle & large enterprises
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
