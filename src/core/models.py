"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.core.database import Base


class SourceType(str):
    """Enumeration of supported job sources/ATS types."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    SMARTRECRUITERS = "smartrecruiters"
    WORKDAY = "workday"
    GENERIC = "generic"


class EmploymentType(str):
    """Employment type enumeration."""

    INTERNSHIP = "internship"
    FULL_TIME = "full_time"
    CO_OP = "co_op"
    PART_TIME = "part_time"
    CONTRACT = "contract"


class Job(Base):
    """Job posting model."""

    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source identification
    source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(255), nullable=False)
    
    # Job details
    company = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    remote = Column(Boolean, default=False)
    employment_type = Column(String(50), nullable=True)
    
    # Dates
    posted_at = Column(DateTime(timezone=True), nullable=True)
    first_seen_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Content
    url = Column(Text, nullable=False)
    description_md = Column(Text, nullable=True)
    
    # Deduplication and versioning
    hash_stable = Column(String(64), nullable=False, index=True)
    hash_full = Column(String(64), nullable=False)
    
    # Status and categorization
    is_active = Column(Boolean, default=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Metadata
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    versions = relationship("JobVersion", back_populates="job", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="job", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_source_source_id"),
        Index("idx_jobs_company_title", "company", "title"),
        Index("idx_jobs_location", "location"),
        Index("idx_jobs_posted_at", "posted_at"),
        Index("idx_jobs_tags", "tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, company={self.company}, title={self.title})>"


class JobVersion(Base):
    """Job version history for tracking changes."""

    __tablename__ = "job_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Version tracking
    hash_full = Column(String(64), nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Change data
    diff_json = Column(JSONB, nullable=True)
    snapshot = Column(JSONB, nullable=True)
    
    # Relationship
    job = relationship("Job", back_populates="versions")
    
    __table_args__ = (Index("idx_job_versions_job_id", "job_id"),)

    def __repr__(self) -> str:
        return f"<JobVersion(id={self.id}, job_id={self.job_id}, captured_at={self.captured_at})>"


class Watchlist(Base):
    """Company watchlist configuration."""

    __tablename__ = "watchlist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Company details
    company = Column(String(255), nullable=False, unique=True, index=True)
    careers_url = Column(Text, nullable=True)
    ats_type = Column(String(50), nullable=False)
    
    # Filters
    roles_include = Column(ARRAY(String), nullable=True)
    locations = Column(ARRAY(String), nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    internship_term = Column(ARRAY(String), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Additional config
    config = Column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Watchlist(company={self.company}, ats_type={self.ats_type})>"


class Alert(Base):
    """Alert/notification tracking."""

    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # 'new', 'updated'
    sent_via = Column(String(50), nullable=False)  # 'slack', 'email', 'pushover'
    sent_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(String(50), nullable=False, default="sent")  # 'sent', 'failed', 'pending'
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Additional data
    alert_metadata = Column(JSONB, nullable=True)
    
    # Relationship
    job = relationship("Job", back_populates="alerts")
    
    __table_args__ = (
        Index("idx_alerts_job_id", "job_id"),
        Index("idx_alerts_sent_at", "sent_at"),
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, job_id={self.job_id}, type={self.alert_type}, via={self.sent_via})>"
