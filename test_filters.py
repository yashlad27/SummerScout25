#!/usr/bin/env python3
"""Quick test script to verify filter fixes are working correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingest.classifier import JobFilter
from src.ingest.schemas import NormalizedJob
from datetime import datetime


def test_job(title: str, location: str = "", description: str = "") -> dict:
    """Test a job title and location against the filters."""
    job = NormalizedJob(
        source="test",
        source_id="test123",
        company="Test Company",
        title=title,
        location=location,
        remote=False,
        employment_type="internship",
        posted_at=datetime.now(),
        url="https://test.com",
        description_md=description,
        hash_stable="test",
        hash_full="test",
        category=None,
        tags=[],
        raw_data={},
        country="us"
    )
    
    job_filter = JobFilter()
    should_include, reason = job_filter.should_include(job)
    
    return {
        "title": title,
        "location": location,
        "should_include": should_include,
        "reason": reason,
        "is_internship": job_filter._is_internship(job),
        "has_negatives": job_filter._has_negative_keywords(job),
        "location_ok": job_filter._location_allowed(job),
    }


def main():
    """Run test cases."""
    print("=" * 80)
    print("FILTER TEST SUITE")
    print("=" * 80)
    print()
    
    test_cases = [
        # Should PASS (Masters-eligible US internships)
        ("Software Engineer Intern - Summer 2026", "New York, NY", ""),
        ("Data Science Intern (2026 Start)", "San Francisco, California", ""),
        ("Machine Learning Intern", "Boston, MA", "Seeking Masters students"),
        ("Quantitative Research Intern", "Chicago, IL", "Graduate student internship"),
        ("Graduate Software Engineer", "Remote, US", ""),
        
        # Should FAIL (PhD-only)
        ("PhD Intern", "New York, NY", ""),
        ("Quantitative Research Engineer – PhD Graduate", "Miami, New York", ""),
        ("Software Developer Ph.D. Intern", "Chicago", ""),
        ("Graduate Intern", "Seattle", "PhD student in Computer Science"),
        
        # Should FAIL (International locations)
        ("Software Engineering Intern (2026)", "Belgrade, Serbia", ""),
        ("Product Management Intern - Amsterdam", "Amsterdam, Netherlands", ""),
        ("Software Engineer II, Frontend", "Remote Poland", ""),
        ("Data Science Intern", "Toronto, Canada", ""),
        ("ML Intern", "Singapore", ""),
        
        # Should FAIL (Generic pages)
        ("Internships", "", ""),
        ("Internship Programs", "", ""),
        ("Join our Talent Community for students & graduates", "", ""),
        ("student and internship opportunities", "", ""),
        
        # Should FAIL (Undergrad-only)
        ("Undergraduate Intern", "New York", ""),
        
        # Should FAIL (Senior positions)
        ("Senior Software Engineer", "San Francisco", ""),
        ("Staff Engineer", "Seattle", ""),
        
        # Edge cases
        ("Software Engineering Intern (2026) - Multiple Locations", "Bellevue, Washington; Mountain View, California; Vancouver, Canada", ""),
        ("Quantitative Analyst Intern", "New York", "For Masters or PhD students"),
    ]
    
    passed = []
    failed = []
    
    for title, location, description in test_cases:
        result = test_job(title, location, description)
        
        # Determine expected outcome
        title_lower = title.lower()
        location_lower = location.lower()
        desc_lower = description.lower()
        
        # Should pass if:
        # - Has intern/graduate in title
        # - US location
        # - No PhD keywords
        # - Not generic page
        # - Not undergrad-only
        # - Not senior
        
        expected_pass = (
            ("intern" in title_lower or "graduate" in title_lower) and
            ("phd" not in title_lower and "ph.d" not in title_lower and "doctoral" not in title_lower) and
            ("phd" not in desc_lower) and
            not any(country in f"{title_lower} {location_lower}" for country in [
                "serbia", "poland", "spain", "germany", "france", "netherlands",
                "denmark", "canada", "singapore", "toronto", "amsterdam", "belgrade"
            ]) and
            title_lower not in ["internships", "internship programs"] and
            "join.*talent.*community" not in title_lower and
            "undergraduate" not in title_lower and
            "senior" not in title_lower and
            "staff" not in title_lower
        )
        
        status = "✅ PASS" if result["should_include"] == expected_pass else "❌ FAIL"
        
        if result["should_include"] == expected_pass:
            passed.append(result)
        else:
            failed.append(result)
        
        print(f"{status} | {result['should_include']} | {title[:60]}")
        print(f"         Location: {location[:50]}")
        print(f"         Reason: {result['reason']}")
        print(f"         Internship={result['is_internship']}, "
              f"Negatives={result['has_negatives']}, "
              f"Location={result['location_ok']}")
        print()
    
    print("=" * 80)
    print(f"SUMMARY: {len(passed)}/{len(test_cases)} tests passed")
    print("=" * 80)
    
    if failed:
        print("\n❌ FAILED TESTS:")
        for result in failed:
            print(f"  - {result['title']}")
            print(f"    Reason: {result['reason']}")


if __name__ == "__main__":
    main()
