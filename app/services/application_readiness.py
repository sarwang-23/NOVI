from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.application import Application, ApplicationRequirement

class ApplicationReadinessService:
    @staticmethod
    def assess_readiness(db: Session, application_id: int, student_id: int) -> dict:
        """
        Assesses if an application is ready for submission based on requirements.
        """
        application = db.scalar(
            select(Application)
            .where(Application.id == application_id)
            .where(Application.student_id == student_id)
        )
        if not application:
            return {}

        requirements = db.scalars(
            select(ApplicationRequirement)
            .where(ApplicationRequirement.application_id == application_id)
        ).all()

        total_reqs = len(requirements)
        completed_reqs = sum(1 for r in requirements if r.status in ("completed", "waived"))
        
        is_ready = False
        if total_reqs > 0 and total_reqs == completed_reqs:
            is_ready = True
            
        readiness_score = int((completed_reqs / total_reqs * 100)) if total_reqs > 0 else 0

        return {
            "application_id": application.id,
            "program_name": application.program_name,
            "status": application.status,
            "readiness_score": readiness_score,
            "is_ready_for_submission": is_ready,
            "pending_requirements": [r.title for r in requirements if r.status == "pending"]
        }
