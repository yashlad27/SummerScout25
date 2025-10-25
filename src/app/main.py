"""FastAPI application (optional API server)."""

from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
import os

from src.core.database import get_db
from src.core.models import Alert, Job
from src.utils.logging_config import setup_logging

setup_logging()

# Get region from environment variable (us or india)
REGION = os.getenv('REGION', 'us')

app = FastAPI(
    title="Job Tracker API",
    description="API for Summer 2026 Internship Job Tracker",
    version="0.1.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get frontend directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount static files for frontend
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    print(f"✅ Frontend mounted at: {FRONTEND_DIR}")
else:
    print(f"⚠️ Frontend directory not found: {FRONTEND_DIR}")


@app.get("/")
def read_root():
    """Serve the frontend dashboard."""
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    print(f"Looking for: {index_file}")
    print(f"Exists: {os.path.exists(index_file)}")
    
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    
    return {
        "message": "Job Tracker API",
        "version": "0.1.0",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "error": f"Frontend not found at {FRONTEND_DIR}"
    }


@app.get("/dashboard")
def dashboard():
    """Serve the frontend dashboard."""
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    
    raise HTTPException(status_code=404, detail=f"Dashboard not found at {FRONTEND_DIR}")


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
    
    # Filter by region
    query = query.filter(Job.country == REGION)
    
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
    total_jobs = db.query(func.count(Job.id)).filter(Job.country == REGION).scalar()
    active_jobs = db.query(func.count(Job.id)).filter(Job.is_active == True, Job.country == REGION).scalar()
    
    # Jobs by company
    jobs_by_company = (
        db.query(Job.company, func.count(Job.id))
        .filter(Job.is_active == True, Job.country == REGION)
        .group_by(Job.company)
        .all()
    )
    
    # Jobs by category
    jobs_by_category = (
        db.query(Job.category, func.count(Job.id))
        .filter(Job.is_active == True, Job.country == REGION)
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
        .filter(Job.is_active == True, Job.country == REGION)
        .group_by(Job.company)
        .order_by(desc("job_count"))
        .all()
    )
    
    return {
        "companies": [
            {"name": company, "job_count": count} for company, count in companies
        ]
    }


@app.get("/scraper-status")
def scraper_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get scraper status - last run and next scheduled run.
    
    Args:
        db: Database session
        
    Returns:
        Scraper status information
    """
    from datetime import timedelta, timezone
    
    # Get the most recently created job to determine last scrape
    last_job = db.query(Job).order_by(desc(Job.created_at)).first()
    
    # Get the most recent alert to see when scraper last ran
    last_alert = db.query(Alert).order_by(desc(Alert.sent_at)).first()
    
    # Calculate last scrape time (use the most recent between job creation and alert)
    last_scrape = None
    if last_job and last_alert:
        # Make sure both are timezone-aware
        job_time = last_job.created_at.replace(tzinfo=timezone.utc) if last_job.created_at.tzinfo is None else last_job.created_at
        alert_time = last_alert.sent_at.replace(tzinfo=timezone.utc) if last_alert.sent_at.tzinfo is None else last_alert.sent_at
        last_scrape = max(job_time, alert_time)
    elif last_job:
        last_scrape = last_job.created_at.replace(tzinfo=timezone.utc) if last_job.created_at.tzinfo is None else last_job.created_at
    elif last_alert:
        last_scrape = last_alert.sent_at.replace(tzinfo=timezone.utc) if last_alert.sent_at.tzinfo is None else last_alert.sent_at
    
    # Calculate next scrape (every 4 hours)
    next_scrape = None
    hours_until_next = None
    minutes_until_next = None
    
    if last_scrape:
        next_scrape = last_scrape + timedelta(hours=4)
        now = datetime.now(timezone.utc)
        time_until_next = next_scrape - now
        
        if time_until_next.total_seconds() > 0:
            hours_until_next = int(time_until_next.total_seconds() // 3600)
            minutes_until_next = int((time_until_next.total_seconds() % 3600) // 60)
        else:
            # Scrape is overdue
            hours_until_next = 0
            minutes_until_next = 0
            next_scrape = now  # Should run now
    
    return {
        "last_scrape_at": last_scrape.isoformat() if last_scrape else None,
        "next_scrape_at": next_scrape.isoformat() if next_scrape else None,
        "hours_until_next": hours_until_next,
        "minutes_until_next": minutes_until_next,
        "scrape_interval_hours": 4,
    }
