"""Profile, Experience, Education, and Skill Models"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Index, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Profile(Base):
    """User profile model."""

    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    about_me = Column(Text, nullable=True)
    current_title = Column(String(255), nullable=True)
    years_experience = Column(Integer, nullable=True)
    preferred_contract = Column(String(50), nullable=True)  # CDI, freelance, stage, alternance
    preferred_locations = Column(JSON, default=list, nullable=False)  # List of locations
    salary_min_expectations = Column(Integer, nullable=True)
    available_date = Column(DateTime(timezone=True), nullable=True)
    visa_sponsorship_required = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_profiles_user_id", "user_id"),
        Index("idx_profiles_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, title={self.current_title})>"


class Experience(Base):
    """Work experience model."""

    __tablename__ = "experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, default=list, nullable=False)  # List of tech used
    impact_metrics = Column(JSON, nullable=True)  # JSON with metrics
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="experiences")

    __table_args__ = (
        Index("idx_experiences_profile_id", "profile_id"),
        Index("idx_experiences_start_date", "start_date"),
    )

    def __repr__(self):
        return f"<Experience(title={self.title}, company={self.company})>"


class Education(Base):
    """Education model."""

    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    graduation_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="education")

    __table_args__ = (
        Index("idx_education_profile_id", "profile_id"),
        Index("idx_education_graduation_date", "graduation_date"),
    )

    def __repr__(self):
        return f"<Education(degree={self.degree}, institution={self.institution})>"


class Skill(Base):
    """Skill model."""

    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(String(50), nullable=True)  # junior, mid, senior, expert
    category = Column(String(50), nullable=True)  # technical, soft, language, etc.
    endorsement_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="skills")

    __table_args__ = (
        Index("idx_skills_profile_id", "profile_id"),
        Index("idx_skills_name", "name"),
    )

    def __repr__(self):
        return f"<Skill(name={self.name}, level={self.level})>"
