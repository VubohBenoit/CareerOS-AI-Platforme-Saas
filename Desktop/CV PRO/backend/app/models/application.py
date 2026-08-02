"""Application, ApplicationEmail, and Interview Models"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Application(Base):
    """Job application tracking."""

    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="DRAFT", nullable=False)  # DRAFT, READY, SENT, VIEWED, etc.
    result = Column(String(50), nullable=True)  # pending, rejected, offer, accepted
    cv_version_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    letter_version_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    email_body = Column(Text, nullable=True)
    email_subject = Column(String(500), nullable=True)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    email_opened_at = Column(DateTime(timezone=True), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    interviews = Column(JSONB, default=list, nullable=False)  # List of interview records
    feedback = Column(JSONB, nullable=True)  # Interview feedback as JSON
    tags = Column(JSONB, default=list, nullable=False)  # User-defined tags
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("JobPosting")
    emails = relationship("ApplicationEmail", back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_applications_user_id", "user_id"),
        Index("idx_applications_status", "status"),
        Index("idx_applications_created_at", "created_at"),
        Index("idx_applications_job_id", "job_id"),
    )

    def __repr__(self):
        return f"<Application(id={self.id}, status={self.status})>"


class ApplicationEmail(Base):
    """Email tracking for applications."""

    __tablename__ = "application_emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    email_type = Column(String(50), nullable=False)  # initial, followup_1, followup_2, etc.
    email_sent_at = Column(DateTime(timezone=True), nullable=False)
    email_opened_at = Column(DateTime(timezone=True), nullable=True)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="emails")

    __table_args__ = (
        Index("idx_application_emails_application_id", "application_id"),
        Index("idx_application_emails_email_type", "email_type"),
        Index("idx_application_emails_sent_at", "email_sent_at"),
    )

    def __repr__(self):
        return f"<ApplicationEmail(id={self.id}, type={self.email_type})>"


class Interview(Base):
    """Interview scheduling and tracking."""

    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # phone_screening, technical, round_1, round_2, etc.
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    interviewer_name = Column(String(255), nullable=True)
    interviewer_email = Column(String(255), nullable=True)
    interviewer_title = Column(String(255), nullable=True)
    feedback = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    rating = Column(String(50), nullable=True)  # positive, neutral, negative
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_interviews_application_id", "application_id"),
        Index("idx_interviews_type", "type"),
        Index("idx_interviews_scheduled_at", "scheduled_at"),
    )

    def __repr__(self):
        return f"<Interview(id={self.id}, type={self.type})>"
