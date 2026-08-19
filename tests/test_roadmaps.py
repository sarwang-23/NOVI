import pytest
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.roadmap import Roadmap
from app.main import app


class MockUser:
    def __init__(self, id):
        self.id = id


def _override(user_id):
    return MockUser(id=user_id)


@pytest.fixture
def roadmap_data(db_session):
    u = User(auth0_id="auth0|roadmap_test", email="roadmaptest@example.com", role="student")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    s = Student(user_id=u.id, grade=9)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)

    r1 = Roadmap(student_id=s.id, title="High School Plan", description="4-year plan", current_grade=9, target_grade=12)
    r2 = Roadmap(student_id=s.id, title="Summer Prep", description="Summer program", status="completed")
    db_session.add_all([r1, r2])
    db_session.commit()
    db_session.refresh(r1)
    db_session.refresh(r2)

    return {"user": u, "student": s, "r1": r1, "r2": r2}


@pytest.fixture
def auth_client(client, roadmap_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|roadmap_test")
    yield client
    del app.dependency_overrides[auth0.get_user]


def test_get_my_roadmaps(auth_client):
    response = auth_client.get("/api/v1/roadmaps/me")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_create_roadmap(auth_client):
    response = auth_client.post("/api/v1/roadmaps/me", json={
        "title": "College Prep",
        "description": "Preparing for college applications",
        "current_grade": 10,
        "target_grade": 12,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "College Prep"
    assert data["current_grade"] == 10


def test_update_roadmap(auth_client, roadmap_data):
    r1_id = roadmap_data["r1"].id
    response = auth_client.patch(f"/api/v1/roadmaps/{r1_id}", json={
        "title": "Updated High School Plan",
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated High School Plan"


def test_delete_roadmap(auth_client, roadmap_data):
    r1_id = roadmap_data["r1"].id
    response = auth_client.delete(f"/api/v1/roadmaps/{r1_id}")
    assert response.status_code == 200

    response = auth_client.get("/api/v1/roadmaps/me")
    assert len(response.json()) == 1


def test_delete_nonexistent_roadmap(auth_client):
    response = auth_client.delete("/api/v1/roadmaps/99999")
    assert response.status_code == 404
