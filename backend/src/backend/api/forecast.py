from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.schemas.schemas import ForecastSummary
from backend.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecast", tags=["forecast"])

@router.get("", response_model=ForecastSummary)
def get_forecast(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    return ForecastService.get_forecast(db=db, organization_id=organization_id)
