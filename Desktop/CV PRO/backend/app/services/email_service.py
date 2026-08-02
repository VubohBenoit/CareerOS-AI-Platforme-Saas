"""Email notification service with SendGrid"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SMTP_USER")
        self.sender_password = os.getenv("SMTP_PASSWORD")

    def send_job_match_email(self, to_email: str, job_title: str, company: str, match_score: int):
        """Send job match notification"""
        subject = f"🎯 New Job Match: {job_title} at {company} ({match_score}% match)"
        
        html = f"""
        <html>
            <body style="font-family: Arial; color: #333;">
                <h2>Great News! 🎯</h2>
                <p>We found a job that matches your profile:</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>{job_title}</h3>
                    <p><strong>{company}</strong></p>
                    <p style="font-size: 18px; color: #4CAF50;"><strong>{match_score}% Match</strong></p>
                </div>
                
                <p><a href="https://careerosai.com/jobs" style="background: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">View Job</a></p>
                
                <p style="color: #999; font-size: 12px;">You're receiving this because you have saved searches enabled.</p>
            </body>
        </html>
        """
        
        self._send_email(to_email, subject, html)

    def send_application_update(self, to_email: str, company: str, status: str):
        """Send application status update"""
        subject = f"📋 Application Status Update: {company}"
        
        html = f"""
        <html>
            <body style="font-family: Arial; color: #333;">
                <h2>Application Update</h2>
                <p><strong>{company}</strong> - Status: <strong>{status}</strong></p>
                <p><a href="https://careerosai.com/applications">View All Applications</a></p>
            </body>
        </html>
        """
        
        self._send_email(to_email, subject, html)

    def _send_email(self, to_email: str, subject: str, html: str):
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email
            
            part = MIMEText(html, "html")
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())
                
            print(f"✅ Email sent to {to_email}")
        except Exception as e:
            print(f"❌ Email error: {e}")

email_service = EmailService()
