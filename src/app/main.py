"""FastAPI application (optional API server)."""

from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.models import Alert, Job
from src.utils.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Job Tracker API",
    description="API for Summer 2026 Internship Job Tracker",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Job Tracker API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/jobs")
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    company: str | None = None,
    category: str | None = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List jobs with filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        company: Filter by company name
        category: Filter by category
        is_active: Filter by active status
        db: Database session
        
    Returns:
        Dictionary with jobs and metadata
    """
    query = db.query(Job)
    
    # Apply filters
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    
    if category:
        query = query.filter(Job.category == category)
    
    query = query.filter(Job.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    jobs = query.order_by(desc(Job.posted_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "jobs": [
            {
                "id": str(job.id),
                "company": job.company,
                "title": job.title,
                "location": job.location,
                "remote": job.remote,
                "category": job.category,
                "tags": job.tags,
                "url": job.url,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                "first_seen_at": job.first_seen_at.isoformat(),
            }
            for job in jobs
        ],
    }


@app.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get a specific job by ID.
    
    Args:
        job_id: Job UUID
        db: Database session
        
    Returns:
        Job details
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": str(job.id),
        "source": job.source,
        "source_id": job.source_id,
        "company": job.company,
        "title": job.title,
        "location": job.location,
        "remote": job.remote,
        "employment_type": job.employment_type,
        "category": job.category,
        "tags": job.tags,
        "url": job.url,
        "description_md": job.description_md,
        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
        "first_seen_at": job.first_seen_at.isoformat(),
        "last_seen_at": job.last_seen_at.isoformat(),
        "is_active": job.is_active,
    }


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get tracker statistics.
    
    Args:
        db: Database session
        
    Returns:
        Statistics dictionary
    """
    total_jobs = db.query(func.count(Job.id)).scalar()
    active_jobs = db.query(func.count(Job.id)).filter(Job.is_active == True).scalar()
    
    # Jobs by company
    jobs_by_company = (
        db.query(Job.company, func.count(Job.id))
        .filter(Job.is_active == True)
        .group_by(Job.company)
        .all()
    )
    
    # Jobs by category
    jobs_by_category = (
        db.query(Job.category, func.count(Job.id))
        .filter(Job.is_active == True)
        .group_by(Job.category)
        .all()
    )
    
    # Recent alerts
    recent_alerts = db.query(func.count(Alert.id)).filter(
        Alert.sent_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).scalar()
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "jobs_by_company": {company: count for company, count in jobs_by_company},
        "jobs_by_category": {
            category or "uncategorized": count for category, count in jobs_by_category
        },
        "alerts_sent_today": recent_alerts,
    }


@app.get("/companies")
def list_companies(db: Session = Depends(get_db)) -> dict[str, Any]:
    """List all companies with active jobs.
    
    Args:
        db: Database session
        
    Returns:
        List of companies
    """
    companies = (
        db.query(Job.company, func.count(Job.id).label("job_count"))
        .filter(Job.is_active == True)
        .group_by(Job.company)
        .order_by(desc("job_count"))
        .all()
    )
    
    return {
        "companies": [
            {"name": company, "job_count": count} for company, count in companies
        ]
    }
