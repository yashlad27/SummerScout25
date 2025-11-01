"""URL health monitoring system to track failing job sources."""

from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy import Column, String, DateTime, Integer, Text
from src.core.database import Base, get_db_context
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class URLHealth(Base):
    """Track health status of job source URLs."""
    
    __tablename__ = "url_health"
    
    company = Column(String, primary_key=True)
    ats_type = Column(String, primary_key=True)
    url = Column(String)
    last_success = Column(DateTime, nullable=True)
    last_failure = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    status = Column(String, default="unknown")  # healthy, degraded, failed, unknown
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HealthMonitor:
    """Monitor and track health of job source URLs."""
    
    def __init__(self):
        self.logger = logger
    
    def record_success(self, company: str, ats_type: str, url: str, jobs_found: int = 0) -> None:
        """
        Record successful fetch from a URL.
        
        Args:
            company: Company name
            ats_type: ATS type (generic, greenhouse, lever, etc.)
            url: URL that was fetched
            jobs_found: Number of jobs found
        """
        with get_db_context() as db:
            health = db.query(URLHealth).filter_by(
                company=company,
                ats_type=ats_type
            ).first()
            
            if not health:
                health = URLHealth(
                    company=company,
                    ats_type=ats_type,
                    url=url
                )
                db.add(health)
            
            health.last_success = datetime.utcnow()
            health.success_count += 1
            health.failure_count = 0  # Reset failure count on success
            health.last_error = None
            
            # Update status
            if jobs_found > 0:
                health.status = "healthy"
            else:
                # Successful fetch but no jobs - might be temporary
                health.status = "healthy_no_jobs"
            
            db.commit()
            
            self.logger.debug(f"✅ {company} ({ats_type}): Health recorded as {health.status}")
    
    def record_failure(self, company: str, ats_type: str, url: str, error: str) -> None:
        """
        Record failed fetch from a URL.
        
        Args:
            company: Company name
            ats_type: ATS type
            url: URL that failed
            error: Error message
        """
        with get_db_context() as db:
            health = db.query(URLHealth).filter_by(
                company=company,
                ats_type=ats_type
            ).first()
            
            if not health:
                health = URLHealth(
                    company=company,
                    ats_type=ats_type,
                    url=url
                )
                db.add(health)
            
            health.last_failure = datetime.utcnow()
            health.failure_count += 1
            health.last_error = error[:500]  # Truncate long errors
            
            # Update status based on failure patterns
            if health.failure_count >= 10:
                health.status = "failed"
            elif health.failure_count >= 3:
                health.status = "degraded"
            else:
                health.status = "unstable"
            
            db.commit()
            
            self.logger.warning(f"❌ {company} ({ats_type}): Health status {health.status} (failures: {health.failure_count})")
    
    def get_health_status(self, company: str, ats_type: str) -> Optional[Dict]:
        """
        Get health status for a URL.
        
        Args:
            company: Company name
            ats_type: ATS type
            
        Returns:
            Dictionary with health information or None
        """
        with get_db_context() as db:
            health = db.query(URLHealth).filter_by(
                company=company,
                ats_type=ats_type
            ).first()
            
            if not health:
                return None
            
            return {
                "company": health.company,
                "ats_type": health.ats_type,
                "url": health.url,
                "status": health.status,
                "last_success": health.last_success,
                "last_failure": health.last_failure,
                "failure_count": health.failure_count,
                "success_count": health.success_count,
                "last_error": health.last_error
            }
    
    def get_failing_urls(self, min_failures: int = 3) -> list[Dict]:
        """
        Get all URLs that are failing.
        
        Args:
            min_failures: Minimum number of failures to consider
            
        Returns:
            List of dictionaries with failing URL information
        """
        with get_db_context() as db:
            failing = db.query(URLHealth).filter(
                URLHealth.failure_count >= min_failures
            ).order_by(URLHealth.failure_count.desc()).all()
            
            return [
                {
                    "company": h.company,
                    "ats_type": h.ats_type,
                    "url": h.url,
                    "status": h.status,
                    "failure_count": h.failure_count,
                    "last_error": h.last_error,
                    "last_failure": h.last_failure
                }
                for h in failing
            ]
    
    def get_health_summary(self) -> Dict:
        """
        Get overall health summary.
        
        Returns:
            Dictionary with health statistics
        """
        with get_db_context() as db:
            all_health = db.query(URLHealth).all()
            
            summary = {
                "total": len(all_health),
                "healthy": 0,
                "degraded": 0,
                "failed": 0,
                "unknown": 0
            }
            
            for h in all_health:
                if h.status in ["healthy", "healthy_no_jobs"]:
                    summary["healthy"] += 1
                elif h.status == "degraded" or h.status == "unstable":
                    summary["degraded"] += 1
                elif h.status == "failed":
                    summary["failed"] += 1
                else:
                    summary["unknown"] += 1
            
            return summary
    
    def should_try_fallback(self, company: str, ats_type: str) -> bool:
        """
        Check if we should try a fallback source.
        
        Args:
            company: Company name
            ats_type: ATS type
            
        Returns:
            True if fallback should be tried
        """
        status = self.get_health_status(company, ats_type)
        
        if not status:
            return False
        
        # Try fallback if status is degraded or failed
        return status["status"] in ["degraded", "failed", "unstable"]
