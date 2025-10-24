"""Text processing and normalization utilities."""

import re
from typing import Any

from markdownify import markdownify


def html_to_markdown(html: str | None) -> str:
    """Convert HTML to clean Markdown.
    
    Args:
        html: HTML content
        
    Returns:
        Markdown text
    """
    if not html:
        return ""
    
    # Convert to markdown
    markdown = markdownify(html, heading_style="ATX", bullets="-")
    
    # Clean up excessive newlines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    
    # Remove tracking pixels and other junk
    markdown = re.sub(r"!\[.*?\]\(.*?1x1.*?\)", "", markdown)
    
    # Strip leading/trailing whitespace
    markdown = markdown.strip()
    
    return markdown


def clean_company_name(company: str) -> str:
    """Normalize company name.
    
    Args:
        company: Company name
        
    Returns:
        Cleaned company name
    """
    # Remove legal suffixes
    company = re.sub(r",?\s+(Inc\.?|LLC|Ltd\.?|Corporation|Corp\.?)$", "", company, flags=re.IGNORECASE)
    
    # Strip whitespace
    company = company.strip()
    
    return company


def extract_location_parts(location: str) -> dict[str, str | None]:
    """Parse location string into components.
    
    Args:
        location: Location string (e.g., "New York, NY, USA")
        
    Returns:
        Dictionary with city, state, country
    """
    parts = [p.strip() for p in location.split(",")]
    
    result: dict[str, str | None] = {
        "city": None,
        "state": None,
        "country": None,
    }
    
    if len(parts) >= 1:
        result["city"] = parts[0]
    if len(parts) >= 2:
        result["state"] = parts[1]
    if len(parts) >= 3:
        result["country"] = parts[2]
    
    return result


def is_remote_location(location: str | None) -> bool:
    """Check if location indicates remote work.
    
    Args:
        location: Location string
        
    Returns:
        True if remote, False otherwise
    """
    if not location:
        return False
    
    location_lower = location.lower()
    
    remote_keywords = [
        "remote",
        "work from home",
        "wfh",
        "anywhere",
        "distributed",
        "virtual",
    ]
    
    return any(keyword in location_lower for keyword in remote_keywords)


def extract_year_from_text(text: str) -> int | None:
    """Extract a year (2024-2027) from text.
    
    Args:
        text: Text to search
        
    Returns:
        Year if found, None otherwise
    """
    match = re.search(r"\b(202[4-7])\b", text)
    if match:
        return int(match.group(1))
    return None


def contains_internship_keywords(text: str) -> bool:
    """Check if text contains internship-related keywords.
    
    Args:
        text: Text to check
        
    Returns:
        True if internship keywords found
    """
    text_lower = text.lower()
    
    keywords = [
        "intern",
        "internship",
        "co-op",
        "coop",
        "summer program",
        "student program",
    ]
    
    return any(keyword in text_lower for keyword in keywords)


def contains_senior_keywords(text: str) -> bool:
    """Check if text contains senior/non-entry-level keywords.
    
    Args:
        text: Text to check
        
    Returns:
        True if senior keywords found
    """
    text_lower = text.lower()
    
    keywords = [
        r"\bsenior\b",
        r"\bsr\.\b",
        r"\bstaff\b",
        r"\bprincipal\b",
        r"\blead\b",
        r"\bmanager\b",
        r"\bdirector\b",
        r"\bvp\b",
        r"\bhead of\b",
    ]
    
    return any(re.search(pattern, text_lower) for pattern in keywords)


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[: max_length - len(suffix)] + suffix
