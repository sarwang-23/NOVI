from fastapi import FastAPI, Depends
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine
from app.modules.student.router import router as student_router
from app.core.auth import auth0
from app.modules.auth.router import router as auth_router
from app.modules.goals.router import router as goals_router
from app.modules.roadmap.router import router as roadmap_router
from app.modules.roadmap.plans_router import plans_router as roadmap_plans_router
from app.modules.tasks.router import router as tasks_router
from app.modules.achievements.router import router as achievements_router
from app.modules.projects.router import router as projects_router
from app.modules.certificates.router import router as certificates_router
from app.modules.milestones.router import router as milestone_router
from app.modules.skills.router import router as skills_router
from app.modules.careers.router import router as careers_router
from app.modules.universities.router import router as universities_router
from app.modules.opportunities.router import router as opportunities_router
from app.modules.applications.router import router as applications_router

from app.modules.checkins.router import router as checkins_router
from app.modules.notifications.router import router as notifications_router
from app.modules.novi.router import router as novi_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.parent.router import router as parent_router

from app.modules.admin.students_router import router as admin_students_router
from app.modules.admin.careers_router import router as admin_careers_router
from app.modules.admin.universities_router import router as admin_universities_router
from app.modules.admin.analytics_router import router as admin_analytics_router
from app.modules.admin.audit_router import router as admin_audit_router
from app.modules.organizations.router import router as organizations_router

# Phase 131-140 Routers
from app.modules.organizations.settings_router import router as org_settings_router
from app.modules.onboarding.router import router as onboarding_router
from app.modules.counselor.router import router as counselor_router
from app.modules.counselor.assignment_router import router as counselor_assignment_router
from app.modules.imports.router import router as import_router
from app.modules.dashboard.institution_router import router as institution_dashboard_router
from app.modules.reports.router import router as reports_router
from app.modules.approvals.router import router as approvals_router
from app.modules.subscription.router import router as subscription_router

# Phase 141-150 Routers
from app.modules.integrations.router import router as integrations_router

app = FastAPI(
    title="Novi Backend API",
    description="API for Novi Student Platform",
    version="1.0.0"
)

from app.middleware.enterprise import EnterpriseMiddleware

app.add_middleware(EnterpriseMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(auth_router)
app.include_router(goals_router)
app.include_router(roadmap_router)
app.include_router(roadmap_plans_router)
app.include_router(tasks_router)
app.include_router(achievements_router)
app.include_router(projects_router)
app.include_router(certificates_router)
app.include_router(milestone_router)
app.include_router(skills_router)
app.include_router(careers_router)
app.include_router(universities_router)
app.include_router(opportunities_router)
app.include_router(applications_router)
app.include_router(checkins_router)
app.include_router(notifications_router)
app.include_router(novi_router)
app.include_router(dashboard_router)
app.include_router(parent_router)
app.include_router(admin_students_router)
app.include_router(admin_careers_router)
app.include_router(admin_universities_router)
app.include_router(admin_analytics_router)
app.include_router(admin_audit_router)
app.include_router(organizations_router)

# Enterprise Phase Routers (131-140)
app.include_router(onboarding_router)
app.include_router(org_settings_router)
app.include_router(counselor_router)
app.include_router(counselor_assignment_router)
app.include_router(import_router)
app.include_router(institution_dashboard_router)
app.include_router(reports_router)
app.include_router(approvals_router)
app.include_router(subscription_router)

# Integrations Phase Routers (141-150)
app.include_router(integrations_router)

@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "Novi Backend is running"
    }

@app.get("/api/v1/auth/me")
def me(user=Depends(auth0.get_user)):
    return user




@app.get("/health/database")
def database_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


    return {
        "success": True,
        "message": "Novi Database is connected"
    }
