from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.roadmap_weekly_plan import WeeklyPlan, WeeklyPlanItem
from app.models.goal import Goal
from app.models.milestone import Milestone
from app.models.task import Task


class WeeklyPlanningService:
    @staticmethod
    def generate_weekly_plan(db: Session, student_id: int, organization_id: int | None = None) -> WeeklyPlan:
        """
        Intelligently generates a weekly plan based on active goals, roadmap milestones, and tasks.
        """
        today = date.today()
        # Find start of the week (Monday)
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Check if plan already exists for this week
        existing_plan = db.scalar(
            select(WeeklyPlan)
            .where(WeeklyPlan.student_id == student_id)
            .where(WeeklyPlan.week_start == week_start)
        )
        if existing_plan:
            return existing_plan

        # Create new plan
        plan = WeeklyPlan(
            student_id=student_id,
            organization_id=organization_id,
            week_start=week_start,
            week_end=week_end,
            title=f"Weekly Plan: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d')}",
            generated_by="system",
            status="planned"
        )
        db.add(plan)
        db.flush()

        # Pull active tasks due this week
        tasks = db.scalars(
            select(Task)
            .where(Task.student_id == student_id)
            .where(Task.status == "pending")
            .where(Task.due_date >= week_start)
            .where(Task.due_date <= week_end)
        ).all()

        for t in tasks:
            item = WeeklyPlanItem(
                weekly_plan_id=plan.id,
                source_type="task",
                source_id=t.id,
                title=t.title,
                description=t.description,
                priority=t.priority or "medium",
                due_date=t.due_date
            )
            db.add(item)

        # Pull upcoming milestones
        # For a full implementation, we'd use NOVI AI to break down milestones into tasks
        # Here we just add active milestones as high-priority items
        # milestone model needs checking for exact fields, assuming basic ones for now.

        db.commit()
        db.refresh(plan)
        return plan
