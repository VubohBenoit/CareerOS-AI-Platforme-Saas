"""Audit Logging Model (GDPR Compliance)"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class AuditLog(Base):
    """Audit log for tracking all changes (GDPR requirement)."""

    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_type = Column(String(100), nullable=False)  # User, Profile, Application, etc.
    entity_id = Column(String(500), nullable=False)
    action = Column(String(50), nullable=False)  # create, read, update, delete
    changes = Column(JSON, nullable=True)  # Before/after values
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_log_user_id", "user_id"),
        Index("idx_audit_log_entity", "entity_type", "entity_id"),
        Index("idx_audit_log_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog(user_id={self.user_id}, entity_type={self.entity_type}, action={self.action})>"
