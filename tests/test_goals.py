import pytest
from app.core.auth import auth0
from app.models.user import User
from app.models.goal import Goal
from app.main import app


class MockUser:
    def __init__(self, id):
        self.id = id


def _override(user_id):
    return MockUser(id=user_id)


@pytest.fixture
def goal_data(db_session):
    u = User(auth0_id="auth0|goal_test_user", email="goaltest@example.com", role="student")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    from app.models.student import Student
    s = Student(user_id=u.id, grade=10)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)

    g1 = Goal(student_id=s.id, title="Get into MIT", goal_type="university", status="active")
    g2 = Goal(student_id=s.id, title="Learn Python", goal_type="academic", status="completed")
    db_session.add_all([g1, g2])
    db_session.commit()
    db_session.refresh(g1)
    db_session.refresh(g2)

    return {"user": u, "student": s, "g1": g1, "g2": g2}


@pytest.fixture
def auth_client(client, goal_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|goal_test_user")
    yield client
    del app.dependency_overrides[auth0.get_user]


def test_get_my_goals(auth_client):
    response = auth_client.get("/api/v1/goals/me")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = {g["title"] for g in data}
    assert "Get into MIT" in titles
    assert "Learn Python" in titles


def test_create_goal(auth_client):
    response = auth_client.post("/api/v1/goals/me", json={
        "goal_type": "career",
        "title": "Become a Software Engineer",
        "description": "Study CS at a top university",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Become a Software Engineer"
    assert data["goal_type"] == "career"
    assert data["status"] == "active"


def test_create_goal_invalid_type(auth_client):
    response = auth_client.post("/api/v1/goals/me", json={
        "goal_type": "invalid",
        "title": "Bad Goal",
    })
    assert response.status_code == 422


def test_update_goal(auth_client, goal_data):
    g1_id = goal_data["g1"].id
    response = auth_client.patch(f"/api/v1/goals/me/{g1_id}", json={
        "title": "Get into Stanford",
        "target": "Computer Science",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get into Stanford"
    assert data["target"] == "Computer Science"


def test_update_nonexistent_goal(auth_client):
    response = auth_client.patch("/api/v1/goals/me/99999", json={"title": "Nope"})
    assert response.status_code == 404


def test_delete_goal(auth_client, goal_data):
    g1_id = goal_data["g1"].id
    response = auth_client.delete(f"/api/v1/goals/me/{g1_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify deleted
    response = auth_client.get("/api/v1/goals/me")
    assert len(response.json()) == 1


def test_delete_nonexistent_goal(auth_client):
    response = auth_client.delete("/api/v1/goals/me/99999")
    assert response.status_code == 404
