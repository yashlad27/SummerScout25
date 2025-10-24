"""Pydantic schemas for job data."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RawJob(BaseModel):
    """Raw job data from a scraper before normalization."""
    
    source: str
    source_id: str
    company: str
    title: str
    location: str | None = None
    remote: bool = False
    employment_type: str | None = None
    posted_at: datetime | None = None
    url: str
    description_html: str | None = None
    description_md: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class NormalizedJob(BaseModel):
    """Normalized job data ready for database insertion."""
    
    source: str
    source_id: str
    company: str
    title: str
    location: str | None
    remote: bool
    employment_type: str | None
    posted_at: datetime | None
    url: str
    description_md: str
    hash_stable: str
    hash_full: str
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class WatchlistTarget(BaseModel):
    """Watchlist target configuration."""
    
    company: str
    ats_type: str
    careers_url: str | None = None
    roles_include: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    internship_term: list[str] = Field(default_factory=lambda: ["summer 2026"])
    
    @field_validator("ats_type")
    @classmethod
    def validate_ats_type(cls, v: str) -> str:
        """Validate ATS type."""
        valid_types = ["greenhouse", "lever", "ashby", "smartrecruiters", "workday", "generic", "indeed", "linkedin", "glassdoor"]
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid ATS type: {v}. Must be one of {valid_types}")
        return v.lower()
