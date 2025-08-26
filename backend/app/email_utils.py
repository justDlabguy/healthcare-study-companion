from fastapi import BackgroundTasks
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from .config import settings

logger = logging.getLogger(__name__)

async def send_password_reset_email(email: str, token: str, base_url: str):
    """Send a password reset email with the given token."""
    reset_url = f"{base_url}reset-password?token={token}"
    
    subject = "Password Reset Request"
    body = f"""
    <h2>Password Reset Request</h2>
    <p>You requested a password reset. Click the link below to set a new password:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request this, please ignore this email.</p>
    """
    
    try:
        # In production, replace this with your email sending service (e.g., SendGrid, AWS SES)
        # This is a basic example using SMTP
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
        # Don't raise the error to avoid exposing internal details to the user

# Add these settings to your config.py:
# SMTP_SERVER: str = "smtp.example.com"
# SMTP_PORT: int = 587
# SMTP_USERNAME: Optional[str] = None
# SMTP_PASSWORD: Optional[str] = None
# SMTP_FROM_EMAIL: str = "noreply@example.com"
