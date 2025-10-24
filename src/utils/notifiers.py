"""Notification handlers for Slack, Email, etc."""

import smtplib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import requests
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.models import Alert, Job
from src.utils.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class BaseNotifier(ABC):
    """Base class for notifiers."""
    
    channel: str = "base"
    
    @abstractmethod
    def send(self, job: Job, alert_type: str = "new") -> bool:
        """Send notification for a job.
        
        Args:
            job: Job to notify about
            alert_type: Type of alert ('new' or 'updated')
            
        Returns:
            True if sent successfully
        """
        pass
    
    def _format_message(self, job: Job, alert_type: str) -> dict[str, str]:
        """Format job data into message components.
        
        Args:
            job: Job to format
            alert_type: Type of alert
            
        Returns:
            Dictionary with 'title' and 'body'
        """
        prefix = "🆕 NEW" if alert_type == "new" else "🔄 UPDATED"
        category = f"[{job.category}]" if job.category else ""
        
        title = f"{prefix} {category} {job.title} — {job.company}"
        
        if job.location:
            title += f" ({job.location})"
        
        body_parts = [
            f"**Position:** {job.title}",
            f"**Company:** {job.company}",
        ]
        
        if job.location:
            body_parts.append(f"**Location:** {job.location}")
        
        if job.remote:
            body_parts.append("**Remote:** Yes")
        
        if job.posted_at:
            body_parts.append(f"**Posted:** {job.posted_at.strftime('%Y-%m-%d %H:%M UTC')}")
        
        body_parts.append(f"**URL:** {job.url}")
        body_parts.append(f"**Source:** {job.source}")
        
        if job.tags:
            body_parts.append(f"**Tags:** {', '.join(job.tags)}")
        
        body = "\n".join(body_parts)
        
        return {"title": title, "body": body}


class SlackNotifier(BaseNotifier):
    """Slack webhook notifier."""
    
    channel = "slack"
    
    def __init__(self):
        """Initialize Slack notifier."""
        self.webhook_url = settings.slack_webhook_url
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
    
    def send(self, job: Job, alert_type: str = "new") -> bool:
        """Send notification to Slack.
        
        Args:
            job: Job to notify about
            alert_type: Type of alert
            
        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            logger.error("Cannot send Slack notification: webhook URL not configured")
            return False
        
        message = self._format_message(job, alert_type)
        
        # Build Slack message
        color = "#36a64f" if alert_type == "new" else "#ff9900"
        
        payload = {
            "text": message["title"],
            "attachments": [
                {
                    "color": color,
                    "text": message["body"],
                    "footer": "Job Tracker",
                    "ts": int(datetime.utcnow().timestamp()),
                }
            ],
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Sent Slack notification for {job.company} - {job.title}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False


class EmailNotifier(BaseNotifier):
    """Email notifier via SMTP."""
    
    channel = "email"
    
    def __init__(self):
        """Initialize Email notifier."""
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_pass = settings.smtp_pass
        self.smtp_from = settings.smtp_from
        self.smtp_to = settings.smtp_to
        
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass]):
            logger.warning("Email SMTP settings not fully configured")
    
    def send_batch(self, jobs: list[Job], companies_scanned: list[str] = None) -> bool:
        """Send consolidated email with all jobs.
        
        Args:
            jobs: List of jobs to notify about
            companies_scanned: List of companies that were scanned
            
        Returns:
            True if sent successfully
        """
        if not jobs:
            return True
            
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass]):
            logger.error("Cannot send email: SMTP settings not configured")
            return False
        
        # Group jobs by category
        jobs_by_category = {}
        jobs_by_company = {}
        for job in jobs:
            category = job.category or "Other"
            if category not in jobs_by_category:
                jobs_by_category[category] = []
            jobs_by_category[category].append(job)
            
            # Group by company
            if job.company not in jobs_by_company:
                jobs_by_company[job.company] = []
            jobs_by_company[job.company].append(job)
        
        # Create email subject
        total = len(jobs)
        subject = f"🎯 {total} New Summer 2026 Internship{'s' if total > 1 else ''} Found!"
        
        # Build HTML body
        html_parts = [
            "<html><body style='font-family: Arial, sans-serif;'>",
            f"<h1 style='color: #2c3e50;'>{subject}</h1>",
            f"<p style='color: #7f8c8d;'>Found {total} new internship opportunities from {len(jobs_by_company)} companies across {len(jobs_by_category)} categories</p>",
        ]
        
        # Add scan summary if provided
        if companies_scanned:
            html_parts.append(f"<p style='color: #95a5a6; font-size: 14px;'>✅ Scanned {len(companies_scanned)} companies total</p>")
        
        html_parts.append("<hr style='border: 1px solid #ecf0f1;'/>")
        
        text_parts = [
            f"{subject}\n",
            f"Found {total} new internship opportunities from {len(jobs_by_company)} companies\n",
        ]
        
        if companies_scanned:
            text_parts.append(f"✅ Scanned {len(companies_scanned)} companies total\n")
        
        text_parts.append("="*80 + "\n")
        
        # Add jobs grouped by category
        for category, category_jobs in sorted(jobs_by_category.items()):
            html_parts.append(f"<h2 style='color: #3498db; margin-top: 30px;'>📁 {category.upper().replace('_', ' ')} ({len(category_jobs)} jobs)</h2>")
            text_parts.append(f"\n## {category.upper().replace('_', ' ')} ({len(category_jobs)} jobs)\n")
            
            for job in category_jobs:
                # HTML version
                html_parts.append("<div style='background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db;'>")
                html_parts.append(f"<h3 style='margin: 0 0 10px 0; color: #2c3e50;'>{job.company} - {job.title}</h3>")
                html_parts.append(f"<p style='margin: 5px 0;'><strong>📍 Location:</strong> {job.location or 'Not specified'}</p>")
                if job.remote:
                    html_parts.append("<p style='margin: 5px 0;'><strong>🏠 Remote:</strong> Yes</p>")
                if job.tags:
                    html_parts.append(f"<p style='margin: 5px 0;'><strong>🏷️ Tags:</strong> {', '.join(job.tags)}</p>")
                html_parts.append(f"<p style='margin: 10px 0 0 0;'><a href='{job.url}' style='background: #3498db; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; display: inline-block;'>Apply Now →</a></p>")
                html_parts.append("</div>")
                
                # Text version
                text_parts.append(f"\n• {job.company} - {job.title}")
                text_parts.append(f"  Location: {job.location or 'Not specified'}")
                if job.remote:
                    text_parts.append(f"  Remote: Yes")
                text_parts.append(f"  Apply: {job.url}\n")
        
        # Add scan summary footer
        html_parts.append("<hr style='border: 1px solid #ecf0f1; margin-top: 30px;'/>")
        
        if companies_scanned:
            html_parts.append("<details style='margin-top: 20px;'>")
            html_parts.append("<summary style='cursor: pointer; color: #7f8c8d; font-size: 14px;'>📊 View All Companies Scanned ({} total)</summary>".format(len(companies_scanned)))
            html_parts.append("<div style='margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;'>")
            
            # Group companies by whether they had jobs
            companies_with_jobs = set(jobs_by_company.keys())
            companies_scanned_sorted = sorted(companies_scanned)
            
            for company in companies_scanned_sorted:
                if company in companies_with_jobs:
                    html_parts.append(f"<span style='color: #27ae60; margin-right: 15px;'>✓ {company} ({len(jobs_by_company[company])} jobs)</span>")
                else:
                    html_parts.append(f"<span style='color: #95a5a6; margin-right: 15px;'>○ {company}</span>")
            
            html_parts.append("</div></details>")
            
            text_parts.append("\n" + "="*80 + "\n")
            text_parts.append(f"Companies Scanned ({len(companies_scanned)} total):\n")
            for company in companies_scanned_sorted:
                if company in companies_with_jobs:
                    text_parts.append(f"  ✓ {company} ({len(jobs_by_company[company])} jobs)\n")
                else:
                    text_parts.append(f"  ○ {company}\n")
        
        html_parts.append("<p style='color: #95a5a6; font-size: 12px; margin-top: 20px;'>Automated notification from Job Tracker</p>")
        html_parts.append("</body></html>")
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.smtp_from or self.smtp_user
        msg["To"] = self.smtp_to or self.smtp_user
        
        msg.attach(MIMEText("\n".join(text_parts), "plain"))
        msg.attach(MIMEText("".join(html_parts), "html"))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Sent consolidated email with {total} jobs")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send consolidated email: {e}")
            return False
    
    def send(self, job: Job, alert_type: str = "new") -> bool:
        """Send notification via email.
        
        Args:
            job: Job to notify about
            alert_type: Type of alert
            
        Returns:
            True if sent successfully
        """
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass]):
            logger.error("Cannot send email: SMTP settings not configured")
            return False
        
        message = self._format_message(job, alert_type)
        
        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = message["title"]
        msg["From"] = self.smtp_from or self.smtp_user
        msg["To"] = self.smtp_to or self.smtp_user
        
        # Plain text body
        text_body = message["body"]
        
        # HTML body - format the message body first
        formatted_body = message["body"].replace("**", "<b>").replace("\n", "<br/>")
        
        html_body = f"""
        <html>
        <body>
            <h2>{message["title"]}</h2>
            <div style="font-family: Arial, sans-serif;">
                {formatted_body}
            </div>
            <hr/>
            <p style="color: #666; font-size: 12px;">
                Automated notification from Job Tracker
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Sent email notification for {job.company} - {job.title}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False


class NotificationManager:
    """Manage notifications across multiple channels."""
    
    def __init__(self, db: Session):
        """Initialize notification manager.
        
        Args:
            db: Database session
        """
        self.db = db
        self.notifiers: dict[str, BaseNotifier] = {}
        
        # Initialize configured notifiers
        if settings.slack_webhook_url:
            self.notifiers["slack"] = SlackNotifier()
        
        if settings.smtp_server:
            self.notifiers["email"] = EmailNotifier()
        
        logger.info(f"Initialized notifiers: {list(self.notifiers.keys())}")
    
    def notify_batch(self, jobs: list[Job], companies_scanned: list[str] = None) -> None:
        """Send consolidated notification for multiple jobs.
        
        Args:
            jobs: List of jobs to notify about
            companies_scanned: List of all companies that were scanned
        """
        if not jobs:
            return
        
        # Send batch email if email notifier is configured
        email_notifier = self.notifiers.get("email")
        if email_notifier and hasattr(email_notifier, 'send_batch'):
            success = email_notifier.send_batch(jobs, companies_scanned=companies_scanned)
            
            # Record alerts for all jobs (safely handle session issues)
            try:
                for job in jobs:
                    self._record_alert(
                        job_id=job.id,
                        alert_type="new",
                        channel="email",
                        status="sent" if success else "failed",
                    )
            except Exception as e:
                logger.warning(f"Failed to record alerts (non-critical): {e}")
        
        logger.info(f"Sent batch notification for {len(jobs)} jobs")
    
    def notify(self, job: Job, alert_type: str = "new", channels: list[str] | None = None) -> None:
        """Send notifications for a job.
        
        Args:
            job: Job to notify about
            alert_type: Type of alert ('new' or 'updated')
            channels: Specific channels to use (None = all)
        """
        # Check cooldown to avoid duplicate notifications
        if not self._check_cooldown(job, channels or list(self.notifiers.keys())):
            logger.debug(f"Skipping notification for {job.id} due to cooldown")
            return
        
        # Determine which channels to use
        target_channels = channels or list(self.notifiers.keys())
        
        for channel in target_channels:
            notifier = self.notifiers.get(channel)
            
            if not notifier:
                logger.warning(f"Notifier not configured: {channel}")
                continue
            
            # Send notification
            success = notifier.send(job, alert_type)
            
            # Record alert
            self._record_alert(
                job_id=job.id,
                alert_type=alert_type,
                channel=channel,
                status="sent" if success else "failed",
            )
    
    def _check_cooldown(self, job: Job, channels: list[str], cooldown_hours: int = 24) -> bool:
        """Check if notification cooldown has passed.
        
        Args:
            job: Job to check
            channels: Channels to check
            cooldown_hours: Cooldown period in hours
            
        Returns:
            True if cooldown has passed
        """
        cutoff = datetime.utcnow() - timedelta(hours=cooldown_hours)
        
        # Check if any alert was sent recently
        recent_alert = self.db.query(Alert).filter(
            Alert.job_id == job.id,
            Alert.sent_via.in_(channels),
            Alert.sent_at >= cutoff,
            Alert.status == "sent",
        ).first()
        
        return recent_alert is None
    
    def _record_alert(
        self,
        job_id: str,
        alert_type: str,
        channel: str,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Record an alert in the database.
        
        Args:
            job_id: Job ID
            alert_type: Alert type
            channel: Notification channel
            status: Alert status
            error_message: Error message if failed
        """
        alert = Alert(
            job_id=job_id,
            alert_type=alert_type,
            sent_via=channel,
            status=status,
            error_message=error_message,
        )
        
        self.db.add(alert)
        # Don't commit here - let the caller handle it
        # self.db.commit()
