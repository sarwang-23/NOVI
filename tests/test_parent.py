import pytest
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.parent import Parent, ParentStudent, ParentStudentInvitation
from app.main import app
from datetime import datetime, timedelta
import secrets


class MockUser:
    def __init__(self, id):
        self.id = id


def _override(user_id):
    return MockUser(id=user_id)


@pytest.fixture
def parent_data(db_session):
    # Parent user
    u_parent = User(auth0_id="auth0|parent_user", email="parent@example.com", role="parent", first_name="Parent")
    db_session.add(u_parent)
    db_session.commit()
    db_session.refresh(u_parent)

    parent = Parent(user_id=u_parent.id)
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)

    # Student user
    u_student = User(auth0_id="auth0|student_for_parent", email="student_for_parent@example.com", role="student", first_name="Child")
    db_session.add(u_student)
    db_session.commit()
    db_session.refresh(u_student)

    student = Student(user_id=u_student.id, grade=11)
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    return {
        "parent_user": u_parent,
        "parent": parent,
        "student_user": u_student,
        "student": student,
    }


@pytest.fixture
def parent_client(client, parent_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|parent_user")
    yield client
    del app.dependency_overrides[auth0.get_user]


def test_get_parent_me(parent_client):
    response = parent_client.get("/api/v1/parent/me")
    assert response.status_code == 200
    data = response.json()
    assert data["relationship_status"] is not None


def test_get_parent_students_empty(parent_client):
    response = parent_client.get("/api/v1/parent/students")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0


def test_invite_student(parent_client, parent_data):
    response = parent_client.post("/api/v1/parent/students/invite", json={
        "student_email": "student_for_parent@example.com",
        "relationship_type": "parent",
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["message"] == "Invitation sent successfully"


def test_invite_nonexistent_student(parent_client):
    response = parent_client.post("/api/v1/parent/students/invite", json={
        "student_email": "nonexistent@example.com",
    })
    assert response.status_code == 404


def test_accept_invite(parent_client, parent_data, db_session):
    # Create invitation
    token = secrets.token_urlsafe(32)
    invitation = ParentStudentInvitation(
        parent_id=parent_data["parent"].id,
        student_id=parent_data["student"].id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()

    # Switch to student to accept
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|student_for_parent")

    response = parent_client.post("/api/v1/parent/student-accept-invite", json={
        "token": token,
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Invitation accepted successfully"

    # Switch back to parent
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|parent_user")

    # Verify student is now linked
    response = parent_client.get("/api/v1/parent/students")
    assert len(response.json()["items"]) == 1


def test_accept_expired_invite(parent_client, parent_data, db_session):
    token = secrets.token_urlsafe(32)
    invitation = ParentStudentInvitation(
        parent_id=parent_data["parent"].id,
        student_id=parent_data["student"].id,
        token=token,
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    db_session.add(invitation)
    db_session.commit()

    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|student_for_parent")

    response = parent_client.post("/api/v1/parent/student-accept-invite", json={
        "token": token,
    })
    assert response.status_code == 400

    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|parent_user")
