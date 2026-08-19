from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.core.auth import auth0
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership

# We define a simple permission matrix here. 
# In a robust system, this could be stored in the DB.
ROLE_PERMISSIONS = {
    "super_admin": [
        "students.read", "students.write", "students.delete", "students.import", "students.assign",
        "parents.read", "parents.write", "parents.delete",
        "careers.read", "careers.write", "careers.delete",
        "universities.read", "universities.write", "universities.delete",
        "analytics.read", "ai_monitoring.read", "audit.read",
        "organizations.read", "organizations.write", "settings.write",
        "reports.generate", "ai.configure", "members.read", "members.write"
    ],
    "admin": [
        "students.read", "students.write", "students.assign",
        "parents.read", "parents.write", 
        "careers.read", "careers.write", 
        "universities.read", "universities.write", 
        "analytics.read", "ai_monitoring.read", 
        "organizations.read", "members.read", "reports.generate"
    ],
    "counselor": [
        "students.read", "parents.read", 
        "careers.read", "universities.read",
        "analytics.read", "reports.generate"
    ],
    "content_manager": [
        "careers.read", "careers.write", 
        "universities.read", "universities.write"
    ],
    "analytics_viewer": [
        "analytics.read", "ai_monitoring.read", "reports.generate"
    ],
    "organization_admin": [
        "students.read", "students.write", "students.import", "students.assign",
        "analytics.read", "organizations.read", "settings.write",
        "members.read", "members.write", "reports.generate", "ai.configure"
    ]
}

def require_role(allowed_roles: List[str]):
    def role_checker(user_payload=Depends(auth0.get_user), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.auth0_id == user_payload.id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Super admin bypasses all role checks
        if user.role == "super_admin":
            return user
            
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
            
        return user
    return role_checker

def require_permission(permission: str):
    def permission_checker(user_payload=Depends(auth0.get_user), db: Session = Depends(get_db)):
        user = db.query(User).filter(User.auth0_id == user_payload.id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if user.role == "super_admin":
            return user
            
        user_permissions = ROLE_PERMISSIONS.get(user.role, [])
        if permission not in user_permissions:
            # Check tenant specific roles if applicable (for future expansion)
            # member = db.query(OrganizationMembership)...
            raise HTTPException(status_code=403, detail="Insufficient permissions")
            
        return user
    return permission_checker

def get_current_organization(user_payload=Depends(auth0.get_user), db: Session = Depends(get_db)) -> Optional[Organization]:
    user = db.query(User).filter(User.auth0_id == user_payload.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.status == "active"
    ).first()
    
    if membership:
        return db.query(Organization).filter(Organization.id == membership.organization_id).first()
        
    return None
