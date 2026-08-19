from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.user import User

from app.services.novi_context import NoviContextService

class DashboardService:
    @staticmethod
    def get_dashboard(student: Student, db: Session) -> dict:
        user = db.query(User).filter(User.id == student.user_id).first()
        
        # We reuse existing services to build the dashboard composition safely
        # Note: In a true high-scale environment, we would optimize these into fewer queries,
        # but for V1 we compose them nicely.
        
        # 1. Profile
        profile_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "current_grade": student.grade,
            "curriculum": student.curriculum
        }
        
        # 2. Basic Novi Context (pulls goals, roadmap, checkins, unread notifications)
        base_context = NoviContextService.get_context(student, db)
        
        # 3. Strip out Intelligence integrations that were moved to the ML team
        task_recommendations = []
        career_matches = []
        university_recommendations = []
        goals_overview = []
        
        # Compose Dashboard
        return {
            "student": profile_data,
            "novi": {
                "greeting": f"Hello, {user.first_name}!",
                "message": "Welcome back to NOVI. Let's make today productive."
            },
            "today": {
                "recommendation": task_recommendations[0] if task_recommendations else None
            },
            "goals": goals_overview,
            "roadmap": base_context.get("roadmap"),
            "career_dna": base_context.get("career_dna"),
            "career_matches": career_matches,
            "universities": university_recommendations,
            "passport": base_context.get("passport"),
            "weekly_checkin": base_context.get("latest_checkin"),
            "unread_notifications": base_context.get("unread_notifications_count", 0)
        }
