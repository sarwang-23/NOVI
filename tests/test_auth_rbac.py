import pytest
from app.core.auth import auth0
from app.core.rbac import ROLE_PERMISSIONS
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership
from app.main import app


class MockUser:
    def __init__(self, id):
        self.id = id


def _override(user_id):
    return MockUser(id=user_id)


@pytest.fixture
def rbac_data(db_session):
    # Super admin
    u_super = User(auth0_id="auth0|super_admin", email="super@novi.com", role="super_admin", first_name="Super")
    # Regular admin
    u_admin = User(auth0_id="auth0|admin_user", email="admin@novi.com", role="admin", first_name="Admin")
    # Student (no admin perms)
    u_student = User(auth0_id="auth0|student_user", email="student@novi.com", role="student", first_name="Student")
    # Org admin
    u_org_admin = User(auth0_id="auth0|org_admin", email="orgadmin@novi.com", role="organization_admin", first_name="OrgAdmin")

    db_session.add_all([u_super, u_admin, u_student, u_org_admin])
    db_session.commit()
    for u in [u_super, u_admin, u_student, u_org_admin]:
        db_session.refresh(u)

    org = Organization(name="Test University", slug="test-university", organization_type="school", status="active")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=u_org_admin.id,
        role="organization_admin",
        status="active",
    )
    db_session.add(membership)
    db_session.commit()

    return {
        "super": u_super,
        "admin": u_admin,
        "student": u_student,
        "org_admin": u_org_admin,
        "org": org,
    }


def test_role_permissions_matrix():
    assert "super_admin" in ROLE_PERMISSIONS
    assert "admin" in ROLE_PERMISSIONS
    assert "counselor" in ROLE_PERMISSIONS
    assert "content_manager" in ROLE_PERMISSIONS
    assert "analytics_viewer" in ROLE_PERMISSIONS
    assert "organization_admin" in ROLE_PERMISSIONS

    # Super admin has all critical permissions
    sa_perms = ROLE_PERMISSIONS["super_admin"]
    assert "students.read" in sa_perms
    assert "students.write" in sa_perms
    assert "students.delete" in sa_perms
    assert "organizations.write" in sa_perms
    assert "settings.write" in sa_perms


def test_super_admin_bypass(client, rbac_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|super_admin")
    response = client.get("/api/v1/admin/analytics/overview")
    # Should not get 403
    assert response.status_code != 403
    del app.dependency_overrides[auth0.get_user]


def test_student_no_admin_access(client, rbac_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|student_user")
    response = client.get("/api/v1/admin/analytics/overview")
    assert response.status_code == 403
    del app.dependency_overrides[auth0.get_user]


def test_admin_has_read_access(client, rbac_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|admin_user")
    response = client.get("/api/v1/admin/students")
    # Admin has students.read permission
    assert response.status_code != 403
    del app.dependency_overrides[auth0.get_user]


def test_org_admin_org_endpoint(client, rbac_data):
    app.dependency_overrides[auth0.get_user] = lambda: _override("auth0|org_admin")
    response = client.get("/api/v1/organizations/me")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test University"
    del app.dependency_overrides[auth0.get_user]
