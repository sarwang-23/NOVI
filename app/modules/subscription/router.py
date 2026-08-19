from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.rbac import require_role, get_current_organization
from app.models.subscription_plan import SubscriptionPlan, OrganizationSubscription

router = APIRouter(
    prefix="/api/v1/organization/subscription",
    tags=["Subscription"]
)

@router.get("/plans")
def get_available_plans(db: Session = Depends(get_db)):
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.active == True).all()
    return {"items": plans}

@router.get("/me")
def get_my_subscription(
    admin = Depends(require_role(["organization_admin", "super_admin"])),
    organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    if not organization:
        raise HTTPException(status_code=404, detail="No organization associated")
        
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.organization_id == organization.id
    ).first()
    
    if not subscription:
        return {"status": "none"}
        
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
    
    return {
        "status": subscription.status,
        "plan_name": plan.name if plan else None,
        "max_students": plan.max_students if plan else 0,
        "started_at": subscription.started_at,
        "current_period_end": subscription.current_period_end
    }
