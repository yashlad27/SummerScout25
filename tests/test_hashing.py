"""Tests for hashing utilities."""

import pytest

from src.utils.hashing import (
    compute_description_digest,
    compute_hash_full,
    compute_hash_stable,
    jaccard_similarity,
    normalize_location,
    normalize_text,
    tokenize_title,
)


def test_normalize_text():
    """Test text normalization."""
    assert normalize_text("  Hello   World  ") == "hello world"
    assert normalize_text("Machine Learning") == "machine learning"
    assert normalize_text(None) == ""


def test_normalize_location():
    """Test location normalization."""
    assert normalize_location("New York, NY, USA") == "new york, ny"
    assert normalize_location("NYC") == "new york"
    assert normalize_location("Remote") == "remote"


def test_compute_hash_stable():
    """Test stable hash computation."""
    hash1 = compute_hash_stable(
        title="Software Engineer Intern",
        company="Citadel",
        location="New York",
        url="https://example.com/job/123",
    )
    
    hash2 = compute_hash_stable(
        title="Software Engineer Intern",
        company="Citadel",
        location="New York",
        url="https://example.com/job/123",
    )
    
    # Same inputs should produce same hash
    assert hash1 == hash2
    
    # Different URL should produce different hash
    hash3 = compute_hash_stable(
        title="Software Engineer Intern",
        company="Citadel",
        location="New York",
        url="https://example.com/job/456",
    )
    
    assert hash1 != hash3


def test_jaccard_similarity():
    """Test Jaccard similarity calculation."""
    set1 = {"machine", "learning", "engineer"}
    set2 = {"machine", "learning", "engineer"}
    
    assert jaccard_similarity(set1, set2) == 1.0
    
    set3 = {"data", "scientist"}
    assert jaccard_similarity(set1, set3) == 0.0
    
    set4 = {"machine", "learning"}
    # Intersection: 2, Union: 3
    assert jaccard_similarity(set1, set4) == pytest.approx(2/3, rel=0.01)


def test_tokenize_title():
    """Test title tokenization."""
    tokens = tokenize_title("Machine Learning Intern - Summer 2026")
    
    # Should exclude common words and normalize
    assert "machine" in tokens
    assert "learning" in tokens
    # "intern" and "summer" should be removed
    assert "intern" not in tokens
    assert "summer" not in tokens
