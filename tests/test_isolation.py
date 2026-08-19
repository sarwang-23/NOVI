import pytest
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student
from app.models.goal import Goal
from app.main import app

class MockUser1:
    def __init__(self, id):
        self.id = id

class MockUser2:
    def __init__(self, id):
        self.id = id

def override_get_user_1():
    return MockUser1(id="auth0|111")

def override_get_user_2():
    return MockUser2(id="auth0|222")

@pytest.fixture
def test_data(db_session):
    u1 = User(auth0_id="auth0|111", email="student1@test.com", role="student")
    db_session.add(u1)
    db_session.commit()
    db_session.refresh(u1)
    
    s1 = Student(user_id=u1.id, grade=10)
    db_session.add(s1)
    db_session.commit()
    db_session.refresh(s1)
    
    g1 = Goal(student_id=s1.id, title="Goal 1", goal_type="academic", status="in_progress")
    db_session.add(g1)
    db_session.commit()
    db_session.refresh(g1)
    
    u2 = User(auth0_id="auth0|222", email="student2@test.com", role="student")
    db_session.add(u2)
    db_session.commit()
    db_session.refresh(u2)
    
    s2 = Student(user_id=u2.id, grade=11)
    db_session.add(s2)
    db_session.commit()
    db_session.refresh(s2)
    
    g2 = Goal(student_id=s2.id, title="Goal 2", goal_type="personal", status="in_progress")
    db_session.add(g2)
    db_session.commit()
    db_session.refresh(g2)
    
    return {"u1": u1, "s1": s1, "g1": g1, "u2": u2, "s2": s2, "g2": g2}

def test_tenant_isolation_goals(client, test_data):
    # Log in as Student 1
    app.dependency_overrides[auth0.get_user] = override_get_user_1
    
    response = client.get("/api/v1/goals/me")
    assert response.status_code == 200
    data = response.json()
    
    # Student 1 should only see Goal 1
    assert len(data) == 1
    assert data[0]["title"] == "Goal 1"
    
    # Attempt to access Goal 2 directly
    goal2_id = test_data["g2"].id
    response2 = client.delete(f"/api/v1/goals/me/{goal2_id}")
    assert response2.status_code == 404 # Should be denied
    
    # Switch to Student 2
    app.dependency_overrides[auth0.get_user] = override_get_user_2
    
    response = client.get("/api/v1/goals/me")
    assert response.status_code == 200
    data = response.json()
    
    # Student 2 should only see Goal 2
    assert len(data) == 1
    assert data[0]["title"] == "Goal 2"
    
    # Clean up
    del app.dependency_overrides[auth0.get_user]
