from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.student import Student


def get_student_from_auth(user_payload, db: Session) -> Student:
    """
    Shared dependency: Resolve Auth0 user -> DB User -> Student.
    Raises 404 at each step if not found.
    """
    db_user = db.query(User).filter(User.auth0_id == user_payload.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return student


def get_db_user(user_payload, db: Session) -> User:
    """
    Shared dependency: Resolve Auth0 user -> DB User.
    Raises 404 if not found.
    """
    db_user = db.query(User).filter(User.auth0_id == user_payload.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
