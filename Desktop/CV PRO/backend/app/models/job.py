"""Job Posting Model"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Index, Text, BigInteger, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.database import Base


class JobPosting(Base):
    """Scraped job postings from various sources."""

    __tablename__ = "job_postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(500), nullable=True)  # Source-specific ID
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)  # Full job description
    required_skills = Column(JSON, default=list, nullable=False)  # Extracted skills
    required_technologies = Column(JSON, default=list, nullable=False)  # Tech stack
    required_experience_years = Column(Integer, nullable=True)
    seniority_level = Column(String(50), nullable=True)  # junior, mid, senior, lead
    location = Column(String(255), nullable=False)
    employment_type = Column(String(50), nullable=False)  # CDI, freelance, stage
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="EUR", nullable=False)
    source = Column(String(50), nullable=False)  # LinkedIn, Indeed, WTTJ, etc.
    source_url = Column(String(1000), nullable=True)
    posted_date = Column(DateTime(timezone=True), nullable=False)
    expires_date = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ats_keywords = Column(JSON, default=list, nullable=False)  # Key ATS keywords
    company_metadata = Column(JSON, nullable=True)  # Company info (size, industry, etc.)

    __table_args__ = (
        Index("idx_job_postings_company", "company"),
        Index("idx_job_postings_source", "source"),
        Index("idx_job_postings_posted_date", "posted_date"),
        Index("idx_job_postings_external_id", "external_id"),
    )

    def __repr__(self):
        return f"<JobPosting(id={self.id}, title={self.title}, company={self.company})>"
