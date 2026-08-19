from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.database.base import Base

class OrganizationIntegration(Base):
    __tablename__ = "organization_integrations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # student_information_system, learning_management_system, identity_provider, etc.
    integration_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # name of the provider, e.g., 'powerschool', 'canvas', 'clever'
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # disconnected, pending, connected, error, disabled
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="disconnected")
    
    # Secure storage configuration (MVP uses JSONB, in prod use secure vault for secrets)
    configuration: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class IntegrationSyncJob(Base):
    __tablename__ = "integration_sync_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    integration_id: Mapped[int] = mapped_column(ForeignKey("organization_integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # inbound, outbound
    direction: Mapped[str] = mapped_column(String(50), nullable=False, default="inbound")
    
    # queued, running, completed, failed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    error_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
