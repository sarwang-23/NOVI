"""
Tests for Counselor APIs.
Validates: assignment lookup, note creation, and student isolation.
"""
import pytest
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.goal import Goal
from app.models.organization import Organization, OrganizationMembership
from app.models.counselor_assignment import CounselorProfile, CounselorStudentAssignment
from app.models.counselor_note import CounselorNote
from app.main import app


class MockCounselorUser:
    def __init__(self):
        self.id = "auth0|counselor001"


class MockStudentUser:
    def __init__(self):
        self.id = "auth0|student001"


@pytest.fixture
def counselor_data(db_session):
    # Org
    org = Organization(name="Test School", slug="test-school", organization_type="school", status="active")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    # Counselor user
    c_user = User(auth0_id="auth0|counselor001", email="counselor@test.com", role="counselor")
    db_session.add(c_user)
    db_session.commit()
    db_session.refresh(c_user)

    # Org membership
    membership = OrganizationMembership(user_id=c_user.id, organization_id=org.id, role="counselor", status="active")
    db_session.add(membership)

    # Counselor profile
    profile = CounselorProfile(user_id=c_user.id, organization_id=org.id)
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    # Student user + student
    s_user = User(auth0_id="auth0|student001", email="student@test.com", role="student")
    db_session.add(s_user)
    db_session.commit()
    db_session.refresh(s_user)

    student = Student(user_id=s_user.id, grade=10, organization_id=org.id)
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    # Counselor-student assignment
    assignment = CounselorStudentAssignment(
        counselor_id=c_user.id,
        student_id=student.id,
        organization_id=org.id,
        status="active"
    )
    db_session.add(assignment)
    db_session.commit()

    return {"org": org, "c_user": c_user, "student": student, "s_user": s_user}


def test_counselor_get_assigned_students(client, counselor_data):
    app.dependency_overrides[auth0.get_user] = MockCounselorUser
    
    response = client.get("/api/v1/counselor/students")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["student_id"] == counselor_data["student"].id

    del app.dependency_overrides[auth0.get_user]


def test_counselor_cannot_access_unassigned_student(client, counselor_data):
    app.dependency_overrides[auth0.get_user] = MockCounselorUser

    # Try to get notes for an unassigned student ID (999)
    response = client.get("/api/v1/counselor/students/999/notes")
    assert response.status_code == 403

    del app.dependency_overrides[auth0.get_user]


def test_counselor_add_and_get_note(client, counselor_data):
    app.dependency_overrides[auth0.get_user] = MockCounselorUser
    student_id = counselor_data["student"].id

    # Add a note
    response = client.post(
        f"/api/v1/counselor/students/{student_id}/notes",
        json={"note": "Student is making great progress", "visibility": "counselor_private"}
    )
    assert response.status_code == 200

    # Retrieve notes
    response = client.get(f"/api/v1/counselor/students/{student_id}/notes")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["note"] == "Student is making great progress"

    del app.dependency_overrides[auth0.get_user]
