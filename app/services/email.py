import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    SMTP-based email service for transactional emails.
    Configure via environment variables:
      SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_FROM_NAME
    """

    @staticmethod
    def _get_smtp_config():
        return {
            "host": getattr(settings, "SMTP_HOST", "smtp.gmail.com"),
            "port": int(getattr(settings, "SMTP_PORT", "587")),
            "username": getattr(settings, "SMTP_USERNAME", ""),
            "password": getattr(settings, "SMTP_PASSWORD", ""),
            "from_email": getattr(settings, "SMTP_FROM_EMAIL", "noreply@novi.com"),
            "from_name": getattr(settings, "SMTP_FROM_NAME", "Novi Platform"),
        }

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send an email via SMTP. Returns True on success, False on failure."""
        config = EmailService._get_smtp_config()

        if not config["username"] or not config["password"]:
            logger.warning("[EmailService] SMTP credentials not configured. Skipping email send.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{config['from_name']} <{config['from_email']}>"
        msg["To"] = to_email

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(config["host"], config["port"]) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(config["username"], config["password"])
                server.sendmail(config["from_email"], to_email, msg.as_string())
            logger.info(f"[EmailService] Email sent to {to_email}: {subject}")
            return True
        except Exception as exc:
            logger.error(f"[EmailService] Failed to send email to {to_email}: {exc}")
            return False

    @staticmethod
    def send_parent_invitation(to_email: str, parent_name: str, token: str) -> bool:
        """Send parent invitation email."""
        accept_url = f"{getattr(settings, 'APP_BASE_URL', 'http://localhost:3000')}/parent/accept?token={token}"
        subject = "You've been invited to join Novi as a Parent"
        html_body = f"""
        <h2>Hello {parent_name},</h2>
        <p>You have been invited to join the Novi Student Platform as a parent.</p>
        <p>Click the link below to accept the invitation:</p>
        <p><a href="{accept_url}">Accept Invitation</a></p>
        <p>This link will expire in 7 days.</p>
        <p>Best regards,<br>The Novi Team</p>
        """
        text_body = f"Hello {parent_name},\n\nYou have been invited to join Novi.\nAccept here: {accept_url}\n\nThis link expires in 7 days."
        return EmailService.send_email(to_email, subject, html_body, text_body)

    @staticmethod
    def send_task_completed_notification(to_email: str, student_name: str, task_title: str) -> bool:
        """Send notification when a task is completed."""
        subject = f"Task Completed: {task_title}"
        html_body = f"""
        <h2>Great job, {student_name}!</h2>
        <p>You've completed the task: <strong>{task_title}</strong></p>
        <p>Keep up the great work!</p>
        <p>Best regards,<br>The Novi Team</p>
        """
        return EmailService.send_email(to_email, subject, html_body)

    @staticmethod
    def send_goal_achieved_notification(to_email: str, student_name: str, goal_title: str) -> bool:
        """Send notification when a goal is achieved."""
        subject = f"Goal Achieved: {goal_title}"
        html_body = f"""
        <h2>Congratulations, {student_name}!</h2>
        <p>You've achieved your goal: <strong>{goal_title}</strong></p>
        <p>Keep pushing towards your dreams!</p>
        <p>Best regards,<br>The Novi Team</p>
        """
        return EmailService.send_email(to_email, subject, html_body)

    @staticmethod
    def send_weekly_checkin_reminder(to_email: str, student_name: str) -> bool:
        """Send weekly check-in reminder."""
        subject = "Weekly Check-in Reminder"
        html_body = f"""
        <h2>Hi {student_name},</h2>
        <p>It's time for your weekly check-in! Take a moment to reflect on your progress.</p>
        <p>Log in to complete your check-in.</p>
        <p>Best regards,<br>The Novi Team</p>
        """
        return EmailService.send_email(to_email, subject, html_body)
