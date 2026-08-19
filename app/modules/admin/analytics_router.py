from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_permission, get_current_organization
from app.services.platform_analytics import PlatformAnalyticsService

router = APIRouter(
    prefix="/api/v1/admin/analytics",
    tags=["Admin Analytics"]
)

@router.get("/overview")
def get_analytics_overview(
    admin_user = Depends(require_permission("analytics.read")),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    return PlatformAnalyticsService.get_overview(db, organization)
