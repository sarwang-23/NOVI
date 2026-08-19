from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.student_outcome import StudentOutcome

class StudentOutcomeService:
    @staticmethod
    def track_outcome(db: Session, student_id: int, outcome_type: str, title: str, description: str = None) -> StudentOutcome:
        """
        Records a positive student outcome (e.g., job offer, admission).
        """
        outcome = StudentOutcome(
            student_id=student_id,
            outcome_type=outcome_type,
            title=title,
            description=description,
            source="system_inference"
        )
        db.add(outcome)
        db.commit()
        db.refresh(outcome)
        return outcome
