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
        self.db.commit()
