from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
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
    db: Session = Depends(get_db),
):
    return FinanceService.get_transactions(
        db=db,
        organization_id=1,
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
    db: Session = Depends(get_db),
):
    return FinanceService.create_transaction(db=db, data=data, organization_id=1)

@router.get("/summary", response_model=FinanceSummary)
def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return FinanceService.get_summary(
        db=db, organization_id=1, start_date=start_date, end_date=end_date
    )

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    return FinanceService.get_categories(db=db, organization_id=1)
