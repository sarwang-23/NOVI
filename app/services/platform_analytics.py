from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.student import Student
from app.models.user import User
from app.models.parent import ParentStudent
from app.models.goal import Goal
from app.models.roadmap import Roadmap
from app.models.organization import Organization

class PlatformAnalyticsService:
    @staticmethod
    def get_overview(db: Session, organization: Organization | None = None) -> dict:
        # Base queries
        student_query = db.query(Student)
        parent_rel_query = db.query(ParentStudent)
        goal_query = db.query(Goal)
        roadmap_query = db.query(Roadmap)
        
        # Apply tenant isolation if organization is specified
        if organization:
            student_query = student_query.filter(Student.organization_id == organization.id)
            
            # Subquery for students in org
            org_students_subq = db.query(Student.id).filter(Student.organization_id == organization.id).subquery()
            
            parent_rel_query = parent_rel_query.filter(ParentStudent.student_id.in_(org_students_subq))
            goal_query = goal_query.filter(Goal.student_id.in_(org_students_subq))
            roadmap_query = roadmap_query.filter(Roadmap.student_id.in_(org_students_subq))

        # Metrics execution
        total_students = student_query.count()
        total_parent_links = parent_rel_query.count()
        
        active_goals = goal_query.filter(Goal.status == "in_progress").count()
        completed_goals = goal_query.filter(Goal.status == "completed").count()
        
        total_roadmaps = roadmap_query.count()
        active_roadmaps = roadmap_query.filter(Roadmap.is_active == True).count()
        
        return {
            "students": {
                "total": total_students,
                "active_this_week": int(total_students * 0.7) # Mock logic
            },
            "parents": {
                "linked_relationships": total_parent_links
            },
            "goals": {
                "active": active_goals,
                "completed": completed_goals
            },
            "roadmaps": {
                "total": total_roadmaps,
                "active": active_roadmaps
            }
        }
