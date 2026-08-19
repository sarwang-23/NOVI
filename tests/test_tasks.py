import pytest
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.task import Task
from app.models.roadmap import Roadmap
from app.main import app


class MockUser:
    def __init__(self, id):
        self.id = id


def _override(user_id):
    return MockUser(id=user_id)


@pytest.fixture
def task_data(db_session):
    u = User(auth0_id="auth0|task_test", email="tasktest@example.com", role="student")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    s = Student(user_id=u.id, grade=10)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)

    r = Roadmap(student_id=s.id, title="My Roadmap")
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)

    t1 = Task(student_id=s.id, roadmap_id=r.id, title="Study calculus", priority="high", status="pending")
    t2 = Task(student_id=s.id, title="Read chapter 5", priority="low", status="completed")
    db_session.add_all([t1, t2])
    db_session.commit()
    db_session.refresh(t1)
    db_session.refresh(t2)

    return {"user": u, "student": s, "roadmap": r, "t1": t1, "t2": t2}


@pytest.fixture
def auth_client(client, task_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|task_test")
    yield client
    del app.dependency_overrides[auth0.get_user]


def test_get_my_tasks(auth_client):
    response = auth_client.get("/api/v1/tasks/me")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_create_task(auth_client, task_data):
    response = auth_client.post("/api/v1/tasks/me", json={
        "title": "Write essay",
        "priority": "high",
        "roadmap_id": task_data["roadmap"].id,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write essay"
    assert data["status"] == "pending"


def test_create_task_invalid_roadmap(auth_client):
    response = auth_client.post("/api/v1/tasks/me", json={
        "title": "Orphan task",
        "roadmap_id": 99999,
    })
    assert response.status_code == 404


def test_get_task(auth_client, task_data):
    t1_id = task_data["t1"].id
    response = auth_client.get(f"/api/v1/tasks/{t1_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Study calculus"


def test_update_task(auth_client, task_data):
    t1_id = task_data["t1"].id
    response = auth_client.patch(f"/api/v1/tasks/{t1_id}", json={
        "priority": "low",
        "description": "Chapters 1-3",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "low"
    assert data["description"] == "Chapters 1-3"


def test_complete_task(auth_client, task_data):
    t1_id = task_data["t1"].id
    response = auth_client.post(f"/api/v1/tasks/{t1_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_skip_task(auth_client, task_data):
    t1_id = task_data["t1"].id
    response = auth_client.post(f"/api/v1/tasks/{t1_id}/skip")
    assert response.status_code == 200
    assert response.json()["status"] == "skipped"


def test_delete_nonexistent_task(auth_client):
    response = auth_client.get("/api/v1/tasks/99999")
    assert response.status_code == 404
