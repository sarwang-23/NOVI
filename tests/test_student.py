import pytest
from app.core.auth import auth0
from app.models.user import User
from app.models.student import Student

class MockUser:
    def __init__(self, id):
        self.id = id

def override_get_user():
    return MockUser(id="auth0|1234567890")

@pytest.fixture
def auth_client(client, db_session):
    # Setup mock user in db
    db_user = User(
        auth0_id="auth0|1234567890",
        email="test_student@example.com",
        role="student"
    )
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    
    student = Student(user_id=db_user.id, grade=9, school="Test School")
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    
    # Override auth
    from app.main import app
    app.dependency_overrides[auth0.get_user] = override_get_user
    
    yield client
    
    # Cleanup
    del app.dependency_overrides[auth0.get_user]

def test_get_my_student(auth_client):
    response = auth_client.get("/api/v1/students/me")
    assert response.status_code == 200
    data = response.json()
    assert data["grade"] == 9
    assert data["school"] == "Test School"

def test_update_my_student(auth_client):
    response = auth_client.patch("/api/v1/students/me", json={
        "grade": 10,
        "school": "Novi High School",
        "curriculum": "IB"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["grade"] == 10
    assert data["school"] == "Novi High School"
