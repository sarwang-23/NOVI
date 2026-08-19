from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.organization_settings import OrganizationSettings
from app.models.subscription_plan import SubscriptionPlan, OrganizationSubscription

class EntitlementService:
    @staticmethod
    def check_feature_access(db: Session, organization_id: int, feature: str):
        """
        Checks if an organization has access to a specific feature, 
        evaluating both explicit feature toggles in settings and subscription limits.
        """
        # Check explicit organization settings first
        settings = db.query(OrganizationSettings).filter(
            OrganizationSettings.organization_id == organization_id
        ).first()
        
        if settings:
            if feature == "ai_chat" and not settings.ai_enabled:
                raise HTTPException(status_code=403, detail="AI functionality is disabled for this organization")
            if feature == "parent_access" and not settings.parent_enabled:
                raise HTTPException(status_code=403, detail="Parent access is disabled for this organization")
            if feature == "counselor_dashboard" and not settings.counselor_enabled:
                raise HTTPException(status_code=403, detail="Counselor features are disabled for this organization")
                
        # Then check subscription plan entitlements
        subscription = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.organization_id == organization_id,
            OrganizationSubscription.status.in_(["active", "trialing"])
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=402, detail="Active subscription required")
            
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
        if not plan or not plan.active:
            raise HTTPException(status_code=402, detail="Invalid or inactive subscription plan")
            
        # If the plan specifies granular feature flags in a JSON dict
        if plan.features and isinstance(plan.features, dict):
            if not plan.features.get(feature, False):
                raise HTTPException(status_code=403, detail=f"Your current plan does not support feature: {feature}")
                
        return True
        
    @staticmethod
    def check_student_limit(db: Session, organization_id: int, current_student_count: int, adding: int = 1):
        """
        Validates if adding N students exceeds the organization's subscription limit.
        """
        subscription = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.organization_id == organization_id,
            OrganizationSubscription.status.in_(["active", "trialing"])
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=402, detail="Active subscription required")
            
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
        if not plan:
            return True # Fallback if missing plan object somehow
            
        if (current_student_count + adding) > plan.max_students:
            raise HTTPException(
                status_code=402, 
                detail=f"Student limit exceeded. Your plan allows up to {plan.max_students} students."
            )
        return True
