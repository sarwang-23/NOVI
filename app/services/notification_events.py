import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.models.student import Student
from app.services.email import EmailService
from app.services.push import PushNotificationService

logger = logging.getLogger(__name__)


class NotificationEventService:
    """
    Centralized service for creating notifications and triggering
    email/push notifications on domain events.
    """

    @staticmethod
    def create_notification(
        db: Session,
        student_id: int,
        title: str,
        message: str,
        notification_type: str = "info",
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
    ) -> Notification:
        """Create an in-app notification record."""
        notification = Notification(
            student_id=student_id,
            title=title,
            message=message,
            notification_type=notification_type,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def _get_student_user(student_id: int, db: Session):
        """Get user associated with a student."""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None, None
        user = db.query(User).filter(User.id == student.user_id).first()
        return student, user

    @staticmethod
    def on_task_completed(db: Session, student_id: int, task_title: str):
        """Triggered when a student completes a task."""
        student, user = NotificationEventService._get_student_user(student_id, db)
        if not student or not user:
            return

        # In-app notification
        NotificationEventService.create_notification(
            db=db,
            student_id=student_id,
            title="Task Completed",
            message=f"You've completed: {task_title}",
            notification_type="achievement",
            reference_type="task",
        )

        # Email
        student_name = getattr(user, "first_name", None) or user.email.split("@")[0]
        EmailService.send_task_completed_notification(user.email, student_name, task_title)

    @staticmethod
    def on_goal_achieved(db: Session, student_id: int, goal_title: str):
        """Triggered when a student achieves a goal."""
        student, user = NotificationEventService._get_student_user(student_id, db)
        if not student or not user:
            return

        NotificationEventService.create_notification(
            db=db,
            student_id=student_id,
            title="Goal Achieved",
            message=f"You've achieved your goal: {goal_title}",
            notification_type="achievement",
            reference_type="goal",
        )

        student_name = getattr(user, "first_name", None) or user.email.split("@")[0]
        EmailService.send_goal_achieved_notification(user.email, student_name, goal_title)

    @staticmethod
    def on_application_status_change(
        db: Session, student_id: int, program_name: str, new_status: str
    ):
        """Triggered when an application status changes."""
        NotificationEventService.create_notification(
            db=db,
            student_id=student_id,
            title="Application Update",
            message=f"Your application for {program_name} is now: {new_status}",
            notification_type="update",
            reference_type="application",
        )

    @staticmethod
    def on_parent_invitation_sent(
        db: Session, student_id: int, parent_email: str, token: str
    ):
        """Triggered when a parent sends an invitation."""
        student, user = NotificationEventService._get_student_user(student_id, db)
        if not student or not user:
            return

        NotificationEventService.create_notification(
            db=db,
            student_id=student_id,
            title="Parent Invitation",
            message=f"A parent has sent you an invitation to connect.",
            notification_type="info",
            reference_type="parent_invitation",
        )

        # Send email to student
        student_name = getattr(user, "first_name", None) or user.email.split("@")[0]
        EmailService.send_parent_invitation(user.email, student_name, token)

    @staticmethod
    def on_counselor_note_added(
        db: Session, student_id: int, counselor_name: str
    ):
        """Triggered when a counselor adds a note about a student."""
        NotificationEventService.create_notification(
            db=db,
            student_id=student_id,
            title="New Counselor Note",
            message=f"{counselor_name} has added a note about your progress.",
            notification_type="info",
            reference_type="counselor_note",
        )

    @staticmethod
    def on_milestone_due_soon(db: Session, student_id: int, milestone_title: str, days_left: int):
        """Triggered when a milestone is due soon."""
        NotificationEventService.create_notification(
            db=db,
            student_id=student_id,
            title="Milestone Due Soon",
            message=f"Milestone '{milestone_title}' is due in {days_left} days.",
            notification_type="reminder",
            reference_type="milestone",
        )
