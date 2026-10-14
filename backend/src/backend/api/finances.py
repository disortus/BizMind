from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.schemas.schemas import (
    TransactionCreate,
    TransactionResponse,
    FinanceSummary,
)
from backend.services.finance_service import FinanceService

router = APIRouter(prefix="/finances", tags=["finances"])

@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(200, le=500),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return FinanceService.get_transactions(
        db=db,
        organization_id=organization_id,
        category=category,
        transaction_type=transaction_type,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

@router.post("", response_model=TransactionResponse)
def create_transaction(
    data: TransactionCreate,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return FinanceService.create_transaction(
        db=db, data=data, organization_id=organization_id
    )

@router.get("/summary", response_model=FinanceSummary)
def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return FinanceService.get_summary(
        db=db, organization_id=organization_id, start_date=start_date, end_date=end_date
    )

@router.get("/categories", response_model=List[str])
def get_categories(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    return FinanceService.get_categories(db=db, organization_id=organization_id)
