"""Job description analysis and metadata extraction."""

import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.ingest.schemas import JobPosting
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class JobAnalyzer:
    """Analyze job descriptions to extract useful metadata."""
    
    # Common tech stacks
    LANGUAGES = [
        'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 'go', 'rust',
        'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql'
    ]
    
    FRAMEWORKS = [
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node\\.?js', 'express',
        'fastapi', '.net', 'rails', 'laravel', 'tensorflow', 'pytorch', 'scikit-learn'
    ]
    
    TOOLS = [
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'jenkins', 'terraform',
        'ansible', 'redis', 'mongodb', 'postgresql', 'mysql', 'elasticsearch'
    ]
    
    SKILLS = [
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
        'devops', 'cloud', 'microservices', 'api', 'rest', 'graphql', 'agile', 'scrum'
    ]
    
    def __init__(self):
        self.logger = logger
    
    def analyze(self, job: JobPosting) -> Dict:
        """
        Analyze job description and extract metadata.
        
        Args:
            job: JobPosting to analyze
            
        Returns:
            Dictionary with extracted metadata
        """
        description = (job.description_md or "").lower()
        
        metadata = {
            "tech_stack": self._extract_tech_stack(description),
            "required_skills": self._extract_skills(description),
            "compensation": self._extract_compensation(description),
            "visa_sponsorship": self._check_visa_sponsorship(description),
            "deadline": self._extract_deadline(description),
            "duration": self._extract_duration(description),
            "start_date": self._extract_start_date(description),
            "seniority_level": self._determine_seniority(job.title, description)
        }
        
        return metadata
    
    def _extract_tech_stack(self, description: str) -> Dict[str, List[str]]:
        """Extract mentioned technologies."""
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "tools": []
        }
        
        for lang in self.LANGUAGES:
            if re.search(r'\b' + lang + r'\b', description, re.IGNORECASE):
                tech_stack["languages"].append(lang.replace('\\', ''))
        
        for framework in self.FRAMEWORKS:
            if re.search(r'\b' + framework + r'\b', description, re.IGNORECASE):
                tech_stack["frameworks"].append(framework.replace('\\', '').replace('.', ''))
        
        for tool in self.TOOLS:
            if re.search(r'\b' + tool + r'\b', description, re.IGNORECASE):
                tech_stack["tools"].append(tool)
        
        return tech_stack
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract required skills."""
        found_skills = []
        
        for skill in self.SKILLS:
            if skill in description:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_compensation(self, description: str) -> Optional[Dict]:
        """Extract compensation information if mentioned."""
        # Look for salary patterns like "$50/hr", "$50-60/hr", "$50,000", etc.
        salary_patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-?\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)?(?:/hr|/hour|per hour)?',
            r'(\d+)\s*-?\s*(\d+)?\s*(?:dollars?|usd)(?:/hr|/hour|per hour)?'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                try:
                    min_comp = match.group(1).replace(',', '')
                    max_comp = match.group(2).replace(',', '') if match.group(2) else min_comp
                    
                    return {
                        "min": float(min_comp),
                        "max": float(max_comp),
                        "currency": "USD"
                    }
                except (ValueError, AttributeError):
                    continue
        
        return None
    
    def _check_visa_sponsorship(self, description: str) -> Optional[bool]:
        """Check if job mentions visa sponsorship."""
        # Positive indicators
        positive_patterns = [
            r'visa sponsor',
            r'will sponsor',
            r'h-?1b sponsor',
            r'opt\s+students\s+welcome',
            r'f-?1\s+visa',
            r'international\s+students\s+encouraged'
        ]
        
        # Negative indicators
        negative_patterns = [
            r'no\s+visa\s+sponsor',
            r'cannot\s+sponsor',
            r'must\s+be\s+authorized\s+to\s+work',
            r'us\s+citizen\s+or\s+permanent\s+resident\s+only',
            r'must\s+have\s+work\s+authorization'
        ]
        
        for pattern in positive_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return True
        
        for pattern in negative_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return False
        
        return None  # Unknown
    
    def _extract_deadline(self, description: str) -> Optional[str]:
        """Extract application deadline if mentioned."""
        # Look for date patterns
        date_patterns = [
            r'deadline[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
            r'apply\s+by[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
            r'applications?\s+close[:\s]+(\w+\s+\d{1,2},?\s+\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_duration(self, description: str) -> Optional[str]:
        """Extract internship duration."""
        duration_patterns = [
            r'(\d+)\s*(?:weeks?|months?)\s+(?:internship|program)',
            r'(?:internship|program)\s+(?:is|lasts?|duration)\s+(\d+)\s*(?:weeks?|months?)',
            r'summer\s+(\d{4})',
            r'fall\s+(\d{4})',
            r'spring\s+(\d{4})'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_start_date(self, description: str) -> Optional[str]:
        """Extract start date if mentioned."""
        start_patterns = [
            r'start\s+date[:\s]+(\w+\s+\d{4})',
            r'starts?[:\s]+(\w+\s+\d{4})',
            r'beginning[:\s]+(\w+\s+\d{4})'
        ]
        
        for pattern in start_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Check for seasonal mentions
        if 'summer 2025' in description or 'summer 2026' in description:
            year_match = re.search(r'summer\s+(\d{4})', description)
            if year_match:
                return f"Summer {year_match.group(1)}"
        
        return None
    
    def _determine_seniority(self, title: str, description: str) -> str:
        """Determine seniority level."""
        title_lower = title.lower()
        desc_lower = description.lower()
        
        # Check for intern/entry level
        if any(keyword in title_lower for keyword in ['intern', 'internship', 'co-op', 'coop']):
            return 'internship'
        
        if any(keyword in title_lower or keyword in desc_lower for keyword in ['entry', 'junior', 'associate', 'new grad']):
            return 'entry_level'
        
        if any(keyword in title_lower or keyword in desc_lower for keyword in ['senior', 'lead', 'principal', 'staff']):
            return 'senior'
        
        return 'mid_level'
