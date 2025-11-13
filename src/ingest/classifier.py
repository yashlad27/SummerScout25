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
        self.visa_config = self.filters.get("visa", {})
    
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
        
        # 4. Check visa requirements (exclude jobs that explicitly don't sponsor)
        if self._excludes_visa_sponsorship(job):
            return False, "no_visa_sponsorship"
        
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
        description = job.description_md or ""
        
        # Check seniority keywords
        seniority_patterns = self.negatives.get("seniority", [])
        for pattern in seniority_patterns:
            if re.search(pattern, title):
                logger.debug(f"Job '{title}' excluded: seniority keyword match")
                return True
        
        # Check non-engineering keywords
        non_engineering = self.negatives.get("non_engineering", [])
        for pattern in non_engineering:
            if re.search(pattern, title):
                logger.debug(f"Job '{title}' excluded: non-engineering keyword")
                return True
        
        # Check PhD-only positions (Masters students not eligible)
        phd_only = self.negatives.get("phd_only", [])
        for pattern in phd_only:
            if re.search(pattern, title) or re.search(pattern, description):
                logger.debug(f"Job '{title}' excluded: PhD-only position")
                return True
        
        # Check undergrad-only positions
        undergrad_only = self.negatives.get("undergrad_only", [])
        for pattern in undergrad_only:
            if re.search(pattern, title):
                logger.debug(f"Job '{title}' excluded: undergrad-only position")
                return True
        
        # Check generic career pages (not actual jobs)
        generic_pages = self.negatives.get("generic_pages", [])
        for pattern in generic_pages:
            if re.search(pattern, title):
                logger.debug(f"Job '{title}' excluded: generic career page")
                return True
        
        return False
    
    def _location_allowed(self, job: NormalizedJob) -> bool:
        """Check if job location is allowed.
        
        Args:
            job: Normalized job
            
        Returns:
            True if location is allowed (US only)
        """
        location = job.location
        title = job.title
        
        # Comprehensive list of non-US countries/cities to reject
        non_us_locations = [
            # European countries
            'germany', 'france', 'netherlands', 'denmark', 'serbia', 'poland', 'spain',
            'belgium', 'switzerland', 'austria', 'sweden', 'norway', 'finland',
            'italy', 'portugal', 'greece', 'ireland', 'czech', 'slovakia', 'hungary',
            'romania', 'bulgaria', 'croatia', 'slovenia',
            # European cities
            'london', 'paris', 'berlin', 'munich', 'amsterdam', 'dublin', 'zurich',
            'stockholm', 'oslo', 'copenhagen', 'warsaw', 'prague', 'barcelona',
            'madrid', 'rome', 'milan', 'vienna', 'brussels', 'aarhus', 'belgrade',
            # Asia Pacific
            'canada', 'india', 'china', 'japan', 'korea', 'singapore', 'australia',
            'new zealand', 'hong kong', 'taiwan', 'thailand', 'vietnam', 'malaysia',
            'philippines', 'indonesia',
            # Asian cities
            'toronto', 'vancouver', 'montreal', 'bangalore', 'mumbai', 'delhi',
            'hyderabad', 'chennai', 'pune', 'beijing', 'shanghai', 'tokyo',
            'seoul', 'sydney', 'melbourne', 'auckland',
            # Middle East / Latin America
            'israel', 'uae', 'dubai', 'saudi arabia', 'brazil', 'mexico',
            'argentina', 'chile', 'colombia', 'tel aviv', 'sao paulo',
            # UK specific
            'uk', 'united kingdom', 'england', 'scotland', 'wales',
        ]
        
        # Check both title and location for non-US indicators
        combined_text = f"{title} {location}".lower()
        
        for non_us_loc in non_us_locations:
            if non_us_loc in combined_text:
                logger.debug(f"Job '{title}' excluded: non-US location '{non_us_loc}'")
                return False
        
        # If no location data, be cautious - only allow if title has clear US indicators
        if not location or not location.strip():
            title_lower = title.lower()
            
            # Check if title has US city/state indicators
            us_quick_check = ['ny', 'nyc', 'california', 'chicago', 'boston', 'seattle',
                              'austin', 'denver', 'atlanta', 'miami', 'sf', 'bay area',
                              'remote, us', 'us remote', 'usa', 'united states']
            
            has_us_indicator = any(indicator in title_lower for indicator in us_quick_check)
            
            if has_us_indicator:
                return True
            else:
                # No location data and no clear US indicator - reject to be safe
                logger.debug(f"Job '{title}' excluded: no location data and no US indicator in title")
                return False
        
        location_lower = location.lower()
        
        # US states and common indicators
        us_indicators = [
            'united states', 'usa', 'u.s.', 'us,',
            # States
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
            'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
            'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
            'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
            'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
            'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina',
            'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania',
            'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas',
            'utah', 'vermont', 'virginia', 'washington', 'west virginia',
            'wisconsin', 'wyoming',
            # Common cities
            'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
            'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville',
            'san francisco', 'columbus', 'fort worth', 'indianapolis', 'charlotte',
            'seattle', 'denver', 'boston', 'detroit', 'portland', 'las vegas',
            'miami', 'atlanta', 'oakland', 'minneapolis', 'tulsa', 'tampa',
            'arlington', 'raleigh', 'pittsburgh', 'cincinnati', 'sacramento',
            # State abbreviations (be careful with these)
            ', ca', ', ny', ', tx', ', fl', ', il', ', pa', ', oh', ', ga',
            ', nc', ', mi', ', nj', ', va', ', wa', ', az', ', ma', ', tn',
            ', in', ', mo', ', md', ', wi', ', mn', ', co', ', al', ', sc',
            'remote, us', 'remote - us', 'remote (us)', 'remote usa'
        ]
        
        # Check if location contains any US indicator
        for indicator in us_indicators:
            if indicator in location_lower:
                return True
        
        # Check for "remote" with US assumption (if it just says "Remote" and nothing else)
        if location_lower == 'remote':
            # Allow plain "Remote" assuming it could be US
            return True
        
        # Explicitly reject non-US countries
        non_us_countries = [
            'canada', 'uk', 'united kingdom', 'england', 'scotland', 'wales',
            'ireland', 'germany', 'france', 'spain', 'italy', 'netherlands',
            'belgium', 'switzerland', 'austria', 'sweden', 'norway', 'denmark',
            'finland', 'poland', 'czech', 'portugal', 'greece', 'hungary',
            'romania', 'bulgaria', 'croatia', 'serbia', 'slovakia', 'slovenia',
            'india', 'china', 'japan', 'korea', 'singapore', 'australia',
            'new zealand', 'brazil', 'mexico', 'argentina', 'chile', 'israel',
            'south africa', 'egypt', 'dubai', 'uae', 'saudi arabia',
            'toronto', 'vancouver', 'montreal', 'london', 'paris', 'berlin',
            'munich', 'amsterdam', 'dublin', 'zurich', 'stockholm', 'oslo',
            'copenhagen', 'warsaw', 'prague', 'barcelona', 'madrid', 'rome',
            'milan', 'tokyo', 'seoul', 'singapore', 'sydney', 'melbourne',
            'auckland', 'bangalore', 'mumbai', 'delhi', 'hyderabad', 'chennai',
            'beijing', 'shanghai', 'hong kong', 'tel aviv'
        ]
        
        for country in non_us_countries:
            if country in location_lower:
                return False
        
        # If we can't determine, reject it (US only policy)
        return False
    
    def _excludes_visa_sponsorship(self, job: NormalizedJob) -> bool:
        """Check if job explicitly excludes visa sponsorship.
        
        Args:
            job: Normalized job
            
        Returns:
            True if job explicitly states no visa sponsorship
        """
        description = job.description_md or ""
        title = job.title
        combined_text = f"{title} {description}".lower()
        
        # Check for negative visa indicators (must exclude these jobs)
        negative_indicators = self.visa_config.get("negative_indicators", [])
        for pattern in negative_indicators:
            if re.search(pattern, combined_text):
                logger.debug(f"Job '{title}' excluded: no visa sponsorship")
                return True
        
        return False
    
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
        
        return tags
