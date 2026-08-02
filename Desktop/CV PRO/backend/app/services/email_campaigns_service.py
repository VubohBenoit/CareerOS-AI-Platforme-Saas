"""Email campaign service for job alert automation"""
from typing import Optional, List
from datetime import datetime
from app.models.user import User
from app.models.job import Job
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailCampaignService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")

    def send_job_alert(self, user_email: str, jobs: List[Job], search_name: str):
        """Send personalized job alert email"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #2563eb;">🎯 New Jobs Match Your Profile</h1>
                    <p>Hi there! We found <strong>{len(jobs)} new job opportunities</strong> for "{search_name}"</p>
                    
                    <div style="border-top: 2px solid #2563eb; margin: 20px 0;">
                        {''.join([f'''
                        <div style="padding: 15px; border-bottom: 1px solid #e0e0e0;">
                            <h3 style="margin: 0 0 5px 0; color: #1e40af;">{job.title}</h3>
                            <p style="margin: 0; color: #666; font-size: 14px;">{job.company}</p>
                            <p style="margin: 5px 0; font-size: 13px;">
                                📍 {job.location} | 💰 ${job.salary_min}-${job.salary_max}
                            </p>
                        </div>
                        ''' for job in jobs[:5]])}
                    </div>
                    
                    <a href="https://careerosai.com/dashboard/jobs" style="display: inline-block; background: #2563eb; color: white; padding: 12px 30px; border-radius: 5px; text-decoration: none; margin-top: 20px;">
                        View All Jobs
                    </a>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        You're receiving this because you created a saved search. 
                        <a href="https://careerosai.com/dashboard/saved-searches" style="color: #2563eb;">Manage preferences</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        self._send_email(user_email, f"New Jobs: {search_name}", html_content)

    def send_weekly_digest(self, user_email: str, stats: dict):
        """Send weekly digest with application stats"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background: white; padding: 30px; max-width: 600px; margin: 0 auto;">
                    <h1>📊 Your Weekly Summary</h1>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                        <div style="background: #e0f2fe; padding: 20px; border-radius: 10px;">
                            <h3 style="color: #0369a1; margin: 0;">Applications</h3>
                            <p style="font-size: 28px; font-weight: bold; margin: 10px 0 0 0;">{stats.get('applications', 0)}</p>
                        </div>
                        <div style="background: #f0fdf4; padding: 20px; border-radius: 10px;">
                            <h3 style="color: #15803d; margin: 0;">Responses</h3>
                            <p style="font-size: 28px; font-weight: bold; margin: 10px 0 0 0;">{stats.get('responses', 0)}</p>
                        </div>
                        <div style="background: #fef3c7; padding: 20px; border-radius: 10px;">
                            <h3 style="color: #b45309; margin: 0;">Interviews</h3>
                            <p style="font-size: 28px; font-weight: bold; margin: 10px 0 0 0;">{stats.get('interviews', 0)}</p>
                        </div>
                        <div style="background: #fce7f3; padding: 20px; border-radius: 10px;">
                            <h3 style="color: #be185d; margin: 0;">Saved Jobs</h3>
                            <p style="font-size: 28px; font-weight: bold; margin: 10px 0 0 0;">{stats.get('saved', 0)}</p>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        
        self._send_email(user_email, "Your Weekly Job Search Summary", html_content)

    def _send_email(self, recipient: str, subject: str, html_content: str):
        """Internal method to send email"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = recipient
            
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient, msg.as_string())
            
            print(f"✅ Email sent to {recipient}: {subject}")
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")

email_campaign_service = EmailCampaignService()
