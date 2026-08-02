"""Document Model (CV, Cover Letter versions)"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Document(Base):
    """Document storage for CVs and cover letters."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # cv, cover_letter
    title = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)  # v1.0, v1.1, etc.
    file_path = Column(String(500), nullable=False)  # S3 path or local path
    file_size = Column(String(50), nullable=True)
    mime_type = Column(String(100), nullable=True)
    status = Column(String(50), default="active", nullable=False)  # active, archived, deleted
    document_metadata = Column(String(1000), nullable=True)  # JSON metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")

    __table_args__ = (
        Index("idx_documents_user_id", "user_id"),
        Index("idx_documents_type", "type"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, type={self.type}, version={self.version})>"
