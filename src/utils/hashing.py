"""Hashing utilities for job deduplication and change detection."""

import hashlib
import re
from typing import Any


def normalize_text(text: str | None) -> str:
    """Normalize text for consistent hashing.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text (lowercase, whitespace collapsed)
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace multiple whitespace with single space
    text = re.sub(r"\s+", " ", text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_location(location: str | None) -> str:
    """Normalize location string for comparison.
    
    Args:
        location: Location string
        
    Returns:
        Normalized location
    """
    if not location:
        return ""
    
    location = normalize_text(location)
    
    # Remove common suffixes
    location = re.sub(r",\s*(usa|us|united states)$", "", location)
    location = re.sub(r",\s*(uk|united kingdom)$", "", location)
    
    # Normalize common abbreviations
    replacements = {
        "nyc": "new york",
        "sf": "san francisco",
        "la": "los angeles",
    }
    
    for abbr, full in replacements.items():
        if location == abbr:
            location = full
            break
    
    return location


def compute_hash_stable(
    title: str,
    company: str,
    location: str | None,
    url: str,
) -> str:
    """Compute stable hash for job identity.
    
    This hash should remain the same even if description or other
    details change. Used for deduplication.
    
    Args:
        title: Job title
        company: Company name
        location: Job location
        url: Job URL
        
    Returns:
        SHA256 hash (hex string)
    """
    # Normalize inputs
    title_norm = normalize_text(title)
    company_norm = normalize_text(company)
    location_norm = normalize_location(location)
    
    # Remove query parameters and fragments from URL
    url_clean = re.sub(r"[?#].*$", "", url)
    url_norm = url_clean.lower().strip()
    
    # Combine fields
    combined = f"{title_norm}|{company_norm}|{location_norm}|{url_norm}"
    
    # Compute hash
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_hash_full(
    hash_stable: str,
    employment_type: str | None,
    posted_at: str | None,
    description_digest: str,
) -> str:
    """Compute full content hash for change detection.
    
    This hash changes when any meaningful field changes.
    
    Args:
        hash_stable: The stable hash
        employment_type: Employment type
        posted_at: Posted date (ISO format)
        description_digest: Digest of description content
        
    Returns:
        SHA256 hash (hex string)
    """
    employment_norm = normalize_text(employment_type or "")
    posted_norm = posted_at or ""
    
    combined = f"{hash_stable}|{employment_norm}|{posted_norm}|{description_digest}"
    
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_description_digest(description: str | None) -> str:
    """Compute a digest of the job description.
    
    Removes formatting and extracts key content for change detection.
    
    Args:
        description: Job description (Markdown)
        
    Returns:
        SHA256 hash of normalized description
    """
    if not description:
        return ""
    
    # Remove markdown formatting
    desc = re.sub(r"[#*_`\[\]()]", "", description)
    
    # Normalize whitespace
    desc = normalize_text(desc)
    
    # Limit length for hash (first 2000 chars of normalized text)
    desc = desc[:2000]
    
    return hashlib.sha256(desc.encode("utf-8")).hexdigest()


def jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity between two sets.
    
    Args:
        set1: First set
        set2: Second set
        
    Returns:
        Jaccard similarity [0.0, 1.0]
    """
    if not set1 and not set2:
        return 1.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def tokenize_title(title: str) -> set[str]:
    """Tokenize job title for similarity comparison.
    
    Args:
        title: Job title
        
    Returns:
        Set of normalized tokens
    """
    # Normalize
    title = normalize_text(title)
    
    # Remove common prefixes/suffixes
    title = re.sub(r"\bintern\b|\binternship\b", "", title)
    title = re.sub(r"\bsummer\b|\b2026\b", "", title)
    title = re.sub(r"[-–—/]", " ", title)
    
    # Split into words
    tokens = title.split()
    
    # Filter short tokens
    tokens = [t for t in tokens if len(t) > 2]
    
    return set(tokens)
