from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.integration import OrganizationIntegration, IntegrationSyncJob

class IntegrationProvider(ABC):
    """
    Generic adapter interface for connecting external systems to NOVI.
    """
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass
        
    @abstractmethod
    def validate(self) -> bool:
        pass
        
    @abstractmethod
    def sync_students(self) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        pass

class GenericIntegrationService:
    @staticmethod
    def process_sync_job(db: Session, job_id: int):
        """
        Idempotent background job to sync data using the correct provider adapter.
        """
        job = db.query(IntegrationSyncJob).filter(IntegrationSyncJob.id == job_id).first()
        if not job or job.status != "queued":
            return
            
        integration = db.query(OrganizationIntegration).filter(OrganizationIntegration.id == job.integration_id).first()
        if not integration or integration.status != "connected":
            job.status = "failed"
            job.error_summary = {"error": "Integration not connected"}
            db.commit()
            return
            
        # In MVP, mock the sync process
        job.status = "completed"
        job.records_processed = 100
        job.records_created = 10
        job.records_updated = 90
        
        db.commit()
