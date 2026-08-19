from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)

class AuthUserResponse(BaseModel):
    id: int
    email: str
    role: str
    auth0_id: str | None = None

    class Config:
        from_attributes = True

@router.post("/sync", response_model=AuthUserResponse)
def sync_user(user=Depends(auth0.get_user), db: Session = Depends(get_db)):
    auth0_id = user.id
    email = user.email or f"{auth0_id}@placeholder.com"

    existing_user = db.query(User).filter(
        User.auth0_id == auth0_id
    ).first()

    if existing_user:
        if user.email and existing_user.email != user.email:
            existing_user.email = user.email
            db.commit()
            db.refresh(existing_user)

        return existing_user

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        existing_user.auth0_id = auth0_id
        db.commit()
        db.refresh(existing_user)
        return existing_user

    new_user = User(
        email=email,
        auth0_id=auth0_id,
        role="student"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    student = Student(user_id=new_user.id)
    db.add(student)
    db.commit()

    return new_user
