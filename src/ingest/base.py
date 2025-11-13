"""Base scraper class for ATS implementations."""

from abc import ABC, abstractmethod
from typing import Any

from src.ingest.schemas import RawJob, WatchlistTarget
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class BaseScraper(ABC):
    """Base class for ATS scrapers."""
    
    source: str = "base"
    
    def __init__(self, target: WatchlistTarget):
        """Initialize scraper.
        
        Args:
            target: Watchlist target configuration
        """
        self.target = target
        self.company = target.company
        self.logger = logger
    
    @abstractmethod
    def fetch(self) -> list[RawJob]:
        """Fetch jobs from the ATS.
        
        Returns:
            List of raw job postings
            
        Raises:
            Exception: On fetch failure
        """
        pass
    
    def _create_raw_job(
        self,
        source_id: str,
        title: str,
        location: str | None,
        url: str,
        posted_at: Any = None,
        description_html: str | None = None,
        employment_type: str | None = None,
        raw_data: dict[str, Any] | None = None,
    ) -> RawJob:
        """Helper to create a RawJob instance.
        
        Args:
            source_id: Unique ID from the source
            title: Job title
            location: Location string
            url: Job posting URL
            posted_at: Posted date
            description_html: HTML description
            employment_type: Employment type
            raw_data: Raw API response data
            
        Returns:
            RawJob instance
        """
        return RawJob(
            source=self.source,
            source_id=source_id,
            company=self.company,
            title=title,
            location=location,
            employment_type=employment_type,
            posted_at=posted_at,
            url=url,
            description_html=description_html,
            raw_data=raw_data or {},
        )
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(company={self.company}, source={self.source})>"
