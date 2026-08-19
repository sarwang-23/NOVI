from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.goal import Goal
from app.models.roadmap import Roadmap
from app.models.milestone import Milestone
from app.models.task import Task
from app.models.achievement import Achievement
from app.models.project import Project
from app.models.certificate import Certificate
from app.models.weekly_checkin import WeeklyCheckin
from app.models.notification import Notification

class NoviContextService:
    @staticmethod
    def get_context(student: Student, db: Session) -> dict:
        # 1. Student Basic
        student_data = {
            "id": student.id,
            "current_grade": student.grade,
            "curriculum": student.curriculum
        }

        # 2. Goals
        goals = db.query(Goal).filter(Goal.student_id == student.id, Goal.status != "completed").all()
        goals_data = [{"id": g.id, "title": g.title, "goal_type": g.goal_type, "status": g.status} for g in goals]

        # 3. Roadmap
        roadmap = db.query(Roadmap).filter(Roadmap.student_id == student.id, Roadmap.status == "active").first()
        roadmap_data = None
        if roadmap:
            milestones = db.query(Milestone).filter(Milestone.roadmap_id == roadmap.id).all()
            tasks = db.query(Task).filter(Task.roadmap_id == roadmap.id, Task.status != "completed").all()
            roadmap_data = {
                "id": roadmap.id,
                "title": roadmap.title,
                "current_grade": roadmap.current_grade,
                "target_grade": roadmap.target_grade,
                "milestone_count": len(milestones),
                "active_tasks_count": len(tasks),
                "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks[:5]] # only top 5 to save context window
            }

        # 4. Career DNA (Removed ML Feature)
        career_dna_data = None

        # 5. Career Passport (Removed ML Feature)
        passport_data = None
        achievements = db.query(Achievement).filter(Achievement.student_id == student.id).all()
        projects = db.query(Project).filter(Project.student_id == student.id).all()
        
        passport_data = {
            "achievements": [{"title": a.title, "category": a.category} for a in achievements],
            "projects": [{"title": p.title, "role": p.role} for p in projects]
        }

        # 6. Weekly Checkins
        latest_checkin = db.query(WeeklyCheckin).filter(WeeklyCheckin.student_id == student.id).order_by(WeeklyCheckin.created_at.desc()).first()
        checkin_data = None
        if latest_checkin:
            checkin_data = {
                "accomplishments": latest_checkin.accomplishments,
                "learnings": latest_checkin.learnings,
                "mood": latest_checkin.mood
            }

        # 7. Notifications
        unread_notifications = db.query(Notification).filter(Notification.student_id == student.id, Notification.is_read == False).count()

        return {
            "student": student_data,
            "goals": goals_data,
            "roadmap": roadmap_data,
            "career_dna": career_dna_data,
            "passport": passport_data,
            "latest_checkin": checkin_data,
            "unread_notifications_count": unread_notifications
        }


class NoviStudentContextBuilder(NoviContextService):
    @staticmethod
    def get_extended_context(student: Student, db: Session) -> dict:
        base_context = NoviContextService.get_context(student, db)
        
        # 1. Success State (Removed ML Feature)
        success_state = None
        
        # 2. Opportunities
        from app.models.opportunity import StudentOpportunity, Opportunity
        student_opps = db.query(StudentOpportunity).filter(StudentOpportunity.student_id == student.id).all()
        opp_ids = [so.opportunity_id for so in student_opps]
        opps = db.query(Opportunity).filter(Opportunity.id.in_(opp_ids)).all()
        opps_data = [{"title": o.title, "type": o.opportunity_type} for o in opps]
        
        base_context["success_state"] = success_state
        base_context["opportunities"] = opps_data
        
        return base_context

