"""Tests for job classifier."""

import pytest

from src.ingest.classifier import JobClassifier, JobFilter
from src.ingest.schemas import NormalizedJob


@pytest.fixture
def ml_job():
    """Create a sample ML job."""
    return NormalizedJob(
        source="greenhouse",
        source_id="123",
        company="Test Company",
        title="Machine Learning Intern - Summer 2026",
        location="New York, NY",
        remote=False,
        employment_type="internship",
        posted_at=None,
        url="https://example.com/job/123",
        description_md="We are looking for a machine learning intern...",
        hash_stable="abc123",
        hash_full="def456",
    )


@pytest.fixture
def senior_job():
    """Create a sample senior job."""
    return NormalizedJob(
        source="lever",
        source_id="456",
        company="Test Company",
        title="Senior Software Engineer",
        location="San Francisco, CA",
        remote=False,
        employment_type="full_time",
        posted_at=None,
        url="https://example.com/job/456",
        description_md="We are hiring a senior engineer...",
        hash_stable="ghi789",
        hash_full="jkl012",
    )


def test_classifier_ml_job(ml_job):
    """Test ML job classification."""
    classifier = JobClassifier()
    category = classifier.classify(ml_job)
    
    assert category == "ml_ai"


def test_filter_includes_internship(ml_job):
    """Test filter includes internship jobs."""
    job_filter = JobFilter()
    should_include, reason = job_filter.should_include(ml_job)
    
    assert should_include is True
    assert reason == "passed"


def test_filter_excludes_senior(senior_job):
    """Test filter excludes senior jobs."""
    job_filter = JobFilter()
    should_include, reason = job_filter.should_include(senior_job)
    
    assert should_include is False
    assert reason == "negative_keywords"


def test_add_tags(ml_job):
    """Test tag addition."""
    job_filter = JobFilter()
    tags = job_filter.add_tags(ml_job)
    
    assert "internship" in tags
    assert "summer-2026" in tags
