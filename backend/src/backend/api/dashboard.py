from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.schemas.schemas import DashboardSummary
from backend.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardSummary)
def get_dashboard(
    period: str = Query("30d", enum=["30d", "90d", "month", "all"]),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return DashboardService.get_dashboard_summary(
        db=db, period=period, organization_id=organization_id
    )
