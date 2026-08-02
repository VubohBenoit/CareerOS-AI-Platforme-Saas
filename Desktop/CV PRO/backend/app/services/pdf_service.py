"""PDF export service for resumes and applications"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

class PDFService:
    @staticmethod
    def generate_application_report(user_name: str, applications: list) -> bytes:
        """Generate PDF report of all applications"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>Job Application Report - {user_name}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Date
        date_text = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal'])
        story.append(date_text)
        story.append(Spacer(1, 12))
        
        # Applications table
        data = [['Company', 'Position', 'Status', 'Applied Date']]
        for app in applications:
            data.append([
                app.get('company', 'N/A'),
                app.get('position', 'N/A'),
                app.get('status', 'N/A'),
                app.get('applied_date', 'N/A')
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_resume_pdf(user_data: dict) -> bytes:
        """Generate PDF resume from user profile"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Header
        name = Paragraph(f"<b>{user_data.get('name', 'N/A')}</b>", styles['Title'])
        contact = Paragraph(
            f"{user_data.get('email', '')} | {user_data.get('phone', '')}", 
            styles['Normal']
        )
        story.append(name)
        story.append(contact)
        story.append(Spacer(1, 12))
        
        # Summary
        if user_data.get('about_me'):
            summary_title = Paragraph("<b>Professional Summary</b>", styles['Heading2'])
            summary = Paragraph(user_data['about_me'], styles['Normal'])
            story.append(summary_title)
            story.append(summary)
            story.append(Spacer(1, 12))
        
        # Skills
        if user_data.get('skills'):
            skills_title = Paragraph("<b>Skills</b>", styles['Heading2'])
            skills = Paragraph(", ".join(user_data['skills']), styles['Normal'])
            story.append(skills_title)
            story.append(skills)
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_service = PDFService()
