import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self, config: dict):
        self.config = config
        self.sender = config.get("sender")
        self.recipient = config.get("recipient")
        # Prefer env var for password
        self.password = os.getenv("SMTP_PASSWORD") or config.get("password")
        self.server = config.get("smtp_server", "smtp.gmail.com")
        self.port = config.get("smtp_port", 587)

    def send_report(self, subject: str, body_markdown: str):
        if not self.password:
            logger.error("No SMTP password provided. Cannot send email.")
            print("SKIPPING EMAIL: No SMTP password found. Set SMTP_PASSWORD env var.")
            return

        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.recipient
        msg['Subject'] = subject

        # Attach body
        # Simple convert to HTML (very basic) or just send text
        # For better formatting, we could use markdown->html lib, but raw markdown is okay for now or wrapped in <pre>
        html_body = f"<html><body><pre style='font-family: sans-serif; white-space: pre-wrap;'>{body_markdown}</pre></body></html>"
        
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)
            logger.info(f"Email sent to {self.recipient}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
