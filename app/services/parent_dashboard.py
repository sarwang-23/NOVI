from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.parent import Parent, ParentStudent
from app.models.student import Student
from app.models.user import User

from app.services.novi_context import NoviContextService
from app.models.goal import Goal

class ParentDashboardService:
    @staticmethod
    def get_dashboard(parent_user: User, db: Session) -> dict:
        parent = db.query(Parent).filter(Parent.user_id == parent_user.id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent profile not found")
            
        # Get all active authorized children
        parent_students = db.query(ParentStudent).filter(
            ParentStudent.parent_id == parent.id,
            ParentStudent.status == "active"
        ).all()
        
        children_data = []
        for rel in parent_students:
            student = db.query(Student).filter(Student.id == rel.student_id).first()
            if not student:
                continue
                
            student_user = db.query(User).filter(User.id == student.user_id).first()
            
            # Fetch base context for child, but filter out private AI fields
            raw_context = NoviContextService.get_context(student, db)
            goals = db.query(Goal).filter(Goal.student_id == student.id, Goal.status == "in_progress").all()
            goals_overview = [{"id": g.id, "title": g.title} for g in goals]
            
            # Construct a privacy-safe view for the parent
            safe_context = {
                "profile": {
                    "id": student.id,
                    "first_name": student_user.first_name if hasattr(student_user, "first_name") else "Student",
                    "grade": student.grade,
                    "school": student.school,
                    "curriculum": student.curriculum
                },
                "goals": goals_overview,
                "roadmap": {
                    "title": raw_context.get("roadmap", {}).get("title"),
                    "status": raw_context.get("roadmap", {}).get("status")
                } if raw_context.get("roadmap") else None,
                "latest_checkin": {
                    "mood": raw_context.get("latest_checkin", {}).get("mood"),
                    "created_at": raw_context.get("latest_checkin", {}).get("created_at")
                } if raw_context.get("latest_checkin") else None,
                "career_dna": {
                    "strengths": raw_context.get("career_dna", {}).get("strengths", []),
                    "interests": raw_context.get("career_dna", {}).get("interests", [])
                } if raw_context.get("career_dna") else None
            }
            
            children_data.append(safe_context)
            
        return {
            "parent_id": parent.id,
            "children": children_data
        }
