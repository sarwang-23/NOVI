from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.certificate import Certificate

router = APIRouter(
    prefix="/api/v1/certificates",
    tags=["Certificates"]
)

class CertificateCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    organization: str = Field(..., min_length=1, max_length=255)
    issue_date: datetime | None = None
    category: str | None = Field(default=None, max_length=100)
    file_url: str | None = Field(default=None, max_length=1000)

class CertificateUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    organization: str | None = Field(default=None, min_length=1, max_length=255)
    issue_date: datetime | None = None
    category: str | None = Field(default=None, max_length=100)
    file_url: str | None = Field(default=None, max_length=1000)

def _get_student(user, db: Session) -> Student:
    db_user = db.query(User).filter(User.auth0_id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(Student).filter(Student.user_id == db_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

def _serialize_certificate(certificate: Certificate):
    return {
        "id": certificate.id,
        "student_id": certificate.student_id,
        "title": certificate.title,
        "organization": certificate.organization,
        "issue_date": certificate.issue_date,
        "category": certificate.category,
        "file_url": certificate.file_url,
        "created_at": certificate.created_at
    }

@router.get("/me")
def get_my_certificates(
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)
    certificates = db.query(Certificate).filter(
        Certificate.student_id == student.id
    ).all()
    
    return [_serialize_certificate(c) for c in certificates]

@router.post("/me", status_code=201)
def create_certificate(
    payload: CertificateCreate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    certificate = Certificate(
        student_id=student.id,
        title=payload.title,
        organization=payload.organization,
        issue_date=payload.issue_date,
        category=payload.category,
        file_url=payload.file_url
    )

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return _serialize_certificate(certificate)

@router.get("/{certificate_id}")
def get_certificate(
    certificate_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.student_id == student.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    return _serialize_certificate(certificate)

@router.patch("/{certificate_id}")
def update_certificate(
    certificate_id: int,
    payload: CertificateUpdate,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.student_id == student.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if payload.title is not None:
        certificate.title = payload.title

    if payload.organization is not None:
        certificate.organization = payload.organization

    if payload.issue_date is not None:
        certificate.issue_date = payload.issue_date

    if payload.category is not None:
        certificate.category = payload.category

    if payload.file_url is not None:
        certificate.file_url = payload.file_url

    db.commit()
    db.refresh(certificate)

    return _serialize_certificate(certificate)

@router.delete("/{certificate_id}")
def delete_certificate(
    certificate_id: int,
    user=Depends(auth0.get_user),
    db: Session = Depends(get_db)
):
    student = _get_student(user, db)

    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id,
        Certificate.student_id == student.id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    db.delete(certificate)
    db.commit()

    return {"success": True, "message": "Certificate deleted successfully"}
