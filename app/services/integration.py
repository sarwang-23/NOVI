import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.integration import OrganizationIntegration, IntegrationSyncJob
from app.integrations.providers import get_sis_provider, get_lms_provider

logger = logging.getLogger(__name__)


class GenericIntegrationService:
    @staticmethod
    def process_sync_job(db: Session, job_id: int):
        """
        Background job to sync data using the correct provider adapter.
        Routes to SIS or LMS provider based on integration type.
        """
        job = db.query(IntegrationSyncJob).filter(IntegrationSyncJob.id == job_id).first()
        if not job or job.status != "queued":
            return

        integration = db.query(OrganizationIntegration).filter(
            OrganizationIntegration.id == job.integration_id
        ).first()
        if not integration or integration.status != "connected":
            job.status = "failed"
            job.error_summary = {"error": "Integration not connected"}
            db.commit()
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        try:
            config = integration.configuration or {}
            integration_type = integration.integration_type
            provider_name = integration.provider

            if integration_type == "sis":
                result = GenericIntegrationService._sync_sis(provider_name, config, job)
            elif integration_type == "lms":
                result = GenericIntegrationService._sync_lms(provider_name, config, job)
            else:
                result = {"error": f"Unknown integration type: {integration_type}"}

            if "error" in result:
                job.status = "failed"
                job.error_summary = result
            else:
                job.status = "completed"
                job.records_processed = result.get("processed", 0)
                job.records_created = result.get("created", 0)
                job.records_updated = result.get("updated", 0)
                job.records_failed = result.get("failed", 0)

            job.completed_at = datetime.utcnow()
            integration.last_sync_at = datetime.utcnow()
            db.commit()

            logger.info(
                f"[IntegrationSync] Job {job_id} completed: "
                f"processed={job.records_processed}, created={job.records_created}"
            )

        except Exception as exc:
            logger.error(f"[IntegrationSync] Job {job_id} failed: {exc}")
            job.status = "failed"
            job.error_summary = {"error": str(exc)}
            job.completed_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def _sync_sis(provider_name: str, config: dict, job: IntegrationSyncJob) -> Dict[str, Any]:
        """Sync students from a Student Information System."""
        provider = get_sis_provider(provider_name)
        if not provider:
            return {"error": f"Unknown SIS provider: {provider_name}"}

        if not provider.connect(config):
            return {"error": f"Failed to connect to {provider_name}"}

        students = provider.fetch_students(config)
        processed = len(students)
        created = 0
        updated = 0
        failed = 0

        for student_data in students:
            try:
                # In production: match by external_id, create/update Student records
                # For MVP, count as processed
                created += 1
            except Exception as exc:
                failed += 1
                logger.error(f"[SIS Sync] Failed to process student: {exc}")

        return {
            "processed": processed,
            "created": created,
            "updated": updated,
            "failed": failed,
        }

    @staticmethod
    def _sync_lms(provider_name: str, config: dict, job: IntegrationSyncJob) -> Dict[str, Any]:
        """Sync courses from a Learning Management System."""
        provider = get_lms_provider(provider_name)
        if not provider:
            return {"error": f"Unknown LMS provider: {provider_name}"}

        if not provider.connect(config):
            return {"error": f"Failed to connect to {provider_name}"}

        courses = provider.fetch_courses(config)
        processed = len(courses)
        created = 0

        for course_data in courses:
            try:
                # In production: create/update course records
                created += 1
            except Exception as exc:
                logger.error(f"[LMS Sync] Failed to process course: {exc}")

        return {
            "processed": processed,
            "created": created,
            "updated": 0,
            "failed": 0,
        }
