"""Job classification and categorization."""

import re
from typing import Any

from src.core.config import get_config_loader
from src.ingest.schemas import NormalizedJob
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class JobClassifier:
    """Classify jobs into categories based on title and description."""
    
    def __init__(self):
        """Initialize classifier with filter configuration."""
        config_loader = get_config_loader()
        self.filters = config_loader.load_filters()
        self.categories = self.filters.get("categories", {})
    
    def classify(self, job: NormalizedJob) -> str | None:
        """Classify job into a category.
        
        Args:
            job: Normalized job
            
        Returns:
            Category name or None if no match
        """
        title = job.title
        description = job.description_md
        
        # Try each category
        for category_name, category_rules in self.categories.items():
            if self._matches_category(title, description, category_rules):
                logger.debug(f"Job '{title}' classified as {category_name}")
                return category_name
        
        logger.debug(f"Job '{title}' did not match any category")
        return None
    
    def _matches_category(
        self,
        title: str,
        description: str,
        rules: dict[str, Any],
    ) -> bool:
        """Check if job matches category rules.
        
        Args:
            title: Job title
            description: Job description
            rules: Category rules (title_any, description_hints)
            
        Returns:
            True if matches
        """
        # Check title patterns
        title_patterns = rules.get("title_any", [])
        for pattern in title_patterns:
            if re.search(pattern, title):
                return True
        
        # If no title match, check description hints as fallback
        description_hints = rules.get("description_hints", [])
        if description_hints and description:
            hint_matches = 0
            for hint in description_hints:
                if re.search(hint, description):
                    hint_matches += 1
            
            # Require at least 2 description hints to match without title match
            if hint_matches >= 2:
                return True
        
        return False


class JobFilter:
    """Filter jobs based on internship status, location, etc."""
    
    def __init__(self):
        """Initialize filter with configuration."""
        config_loader = get_config_loader()
        self.filters = config_loader.load_filters()
        
        self.internship_config = self.filters.get("internship", {})
        self.negatives = self.filters.get("negatives", {})
        self.locations_config = self.filters.get("locations", {})
    
    def should_include(self, job: NormalizedJob) -> tuple[bool, str]:
        """Determine if job should be included.
        
        Args:
            job: Normalized job
            
        Returns:
            Tuple of (should_include, reason)
        """
        # 1. Check if it's an internship
        if not self._is_internship(job):
            return False, "not_internship"
        
        # 2. Check for negative keywords (senior, manager, etc.)
        if self._has_negative_keywords(job):
            return False, "negative_keywords"
        
        # 3. Check location (if configured)
        if not self._location_allowed(job):
            return False, "location_excluded"
        
        return True, "passed"
    
    def _is_internship(self, job: NormalizedJob) -> bool:
        """Check if job is an internship.
        
        Args:
            job: Normalized job
            
        Returns:
            True if internship
        """
        title = job.title
        description = job.description_md
        
        # Check title patterns
        title_patterns = self.internship_config.get("title_patterns", [])
        for pattern in title_patterns:
            if re.search(pattern, title):
                return True
        
        # Check description patterns as fallback
        description_patterns = self.internship_config.get("description_patterns", [])
        for pattern in description_patterns:
            if re.search(pattern, description):
                return True
        
        return False
    
    def _has_negative_keywords(self, job: NormalizedJob) -> bool:
        """Check if job has negative keywords.
        
        Args:
            job: Normalized job
            
        Returns:
            True if has negative keywords
        """
        title = job.title
        
        # Check seniority keywords
        seniority_patterns = self.negatives.get("seniority", [])
        for pattern in seniority_patterns:
            if re.search(pattern, title):
                return True
        
        # Check non-engineering keywords
        non_engineering = self.negatives.get("non_engineering", [])
        for pattern in non_engineering:
            if re.search(pattern, title):
                return True
        
        return False
    
    def _location_allowed(self, job: NormalizedJob) -> bool:
        """Check if job location is allowed.
        
        Args:
            job: Normalized job
            
        Returns:
            True if location is allowed
        """
        location = job.location
        if not location:
            # No location specified - allow it
            return True
        
        location_lower = location.lower()
        
        # Check excluded countries
        excluded_countries = self.locations_config.get("excluded_countries", [])
        for country in excluded_countries:
            if country.lower() in location_lower:
                return False
        
        # Check allowed locations (if specified)
        allowed = self.locations_config.get("allowed", [])
        if allowed:
            # If allowed list exists, location must match one of them
            for allowed_loc in allowed:
                if allowed_loc.lower() in location_lower:
                    return True
            
            # Remote is always allowed
            if job.remote:
                return True
            
            return False
        
        # If no allowed list, default to allowing
        return True
    
    def add_tags(self, job: NormalizedJob) -> list[str]:
        """Add tags to job based on classification.
        
        Args:
            job: Normalized job
            
        Returns:
            List of tags
        """
        tags = []
        
        # Add internship tag
        if self._is_internship(job):
            tags.append("internship")
        
        # Add summer 2026 tag
        title_desc = f"{job.title} {job.description_md}".lower()
        if "summer 2026" in title_desc or "summer '26" in title_desc:
            tags.append("summer-2026")
        
        # Add category tag if classified
        if job.category:
            tags.append(job.category)
        
        # Add remote tag
        if job.remote:
            tags.append("remote")
        
        return tags
