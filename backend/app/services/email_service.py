"""Email notification service"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.enabled = bool(settings.SMTP_HOST and settings.SMTP_USER)
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.from_email = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.EMAILS_FROM_NAME or "LongBark Hosting"
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send an email"""
        if not self.enabled:
            logger.info("Email is not configured, skipping email send")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add plain text part
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server and send
            if self.smtp_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_alert_email(
        self,
        to_email: str,
        site_name: str,
        alert_type: str,
        severity: str,
        message: str
    ) -> bool:
        """Send an alert notification email"""
        subject = f"[{severity.upper()}] {site_name} - {alert_type} Alert"
        
        body = f"""
LongBark Hosting Alert

Site: {site_name}
Alert Type: {alert_type}
Severity: {severity}

Message:
{message}

---
This is an automated alert from LongBark Hosting Manager.
        """
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #d32f2f;">LongBark Hosting Alert</h2>
    <p><strong>Site:</strong> {site_name}</p>
    <p><strong>Alert Type:</strong> {alert_type}</p>
    <p><strong>Severity:</strong> <span style="color: #d32f2f;">{severity.upper()}</span></p>
    <hr>
    <p><strong>Message:</strong></p>
    <p>{message}</p>
    <hr>
    <p style="color: #666; font-size: 12px;">This is an automated alert from LongBark Hosting Manager.</p>
</body>
</html>
        """
        
        return self.send_email([to_email], subject, body, html_body)


# Global instance
email_service = EmailService()
