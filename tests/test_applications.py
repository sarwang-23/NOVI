import pytest
from datetime import date
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.application import Application, ApplicationRequirement
from app.main import app


class MockUser:
    def __init__(self, id):
        self.id = id


def _override(user_id):
    return MockUser(id=user_id)


@pytest.fixture
def app_data(db_session):
    u = User(auth0_id="auth0|app_test", email="apptest@example.com", role="student")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    s = Student(user_id=u.id, grade=12)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)

    a1 = Application(
        student_id=s.id,
        program_name="Computer Science at MIT",
        target_term="Fall 2027",
        application_type="regular",
        application_deadline=date(2027, 1, 1),
        status="in_progress",
    )
    a2 = Application(
        student_id=s.id,
        program_name="Data Science at Stanford",
        status="draft",
    )
    db_session.add_all([a1, a2])
    db_session.commit()
    db_session.refresh(a1)
    db_session.refresh(a2)

    req = ApplicationRequirement(
        application_id=a1.id,
        title="Personal Statement",
        status="pending",
        due_date=date(2026, 12, 15),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    return {"user": u, "student": s, "a1": a1, "a2": a2, "req": req}


@pytest.fixture
def auth_client(client, app_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|app_test")
    yield client
    del app.dependency_overrides[auth0.get_user]


def test_get_my_applications(auth_client):
    response = auth_client.get("/api/v1/applications/me")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_applications_filtered(auth_client):
    response = auth_client.get("/api/v1/applications/me?status=in_progress")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["program_name"] == "Computer Science at MIT"


def test_create_application(auth_client):
    response = auth_client.post("/api/v1/applications/me", json={
        "program_name": "Physics at Caltech",
        "target_term": "Fall 2027",
        "application_type": "early_action",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["program_name"] == "Physics at Caltech"
    assert data["status"] == "draft"


def test_update_application_status(auth_client, app_data):
    a1_id = app_data["a1"].id
    response = auth_client.patch(f"/api/v1/applications/me/{a1_id}", json={
        "status": "submitted",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "submitted"


def test_delete_application(auth_client, app_data):
    a2_id = app_data["a2"].id
    response = auth_client.delete(f"/api/v1/applications/me/{a2_id}")
    assert response.status_code == 200

    response = auth_client.get("/api/v1/applications/me")
    assert len(response.json()) == 1


def test_get_requirements(auth_client, app_data):
    a1_id = app_data["a1"].id
    response = auth_client.get(f"/api/v1/applications/me/{a1_id}/requirements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Personal Statement"


def test_add_requirement(auth_client, app_data):
    a1_id = app_data["a1"].id
    response = auth_client.post(f"/api/v1/applications/me/{a1_id}/requirements", json={
        "title": "Letters of Recommendation",
        "due_date": "2026-12-01",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Letters of Recommendation"


def test_get_timeline(auth_client, app_data):
    response = auth_client.get("/api/v1/applications/me/timeline")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_outcomes_empty(auth_client):
    response = auth_client.get("/api/v1/applications/me/outcomes")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_create_outcome(auth_client):
    response = auth_client.post("/api/v1/applications/me/outcomes", json={
        "outcome_type": "admission",
        "title": "Accepted to MIT",
        "source": "MIT Admissions Office",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Accepted to MIT"
