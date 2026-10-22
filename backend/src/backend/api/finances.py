from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id, get_current_user, require_roles, log_activity
from backend.models.models import User
from backend.schemas.schemas import (
    TransactionCreate,
    TransactionUpdate,
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


@router.get("/export")
def export_finances(
    format: str = Query("xlsx", pattern="^(xlsx|csv)$"),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    content = FinanceService.export_transactions(db=db, organization_id=organization_id, format_type=format)
    media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"finances_org_{organization_id}.{format}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    tx = FinanceService.get_transaction_by_id(db=db, transaction_id=transaction_id, organization_id=organization_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Финансовая операция не найдена")
    return tx


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tx = FinanceService.create_transaction(
        db=db, data=data, organization_id=organization_id
    )
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="create",
        entity_type="financial_transaction",
        entity_id=str(tx.id),
        details=f"Создана операция: {tx.description} на сумму {tx.amount} ₸ ({tx.transaction_type})",
    )
    return tx


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    tx = FinanceService.update_transaction(
        db=db, transaction_id=transaction_id, data=data, organization_id=organization_id
    )
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Финансовая операция не найдена")
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="update",
        entity_type="financial_transaction",
        entity_id=str(tx.id),
        details=f"Обновлена операция #{tx.id}: {tx.description}, сумма {tx.amount} ₸",
    )
    return tx


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    hard_delete: bool = Query(False),
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner"])),
    db: Session = Depends(get_db),
):
    success = FinanceService.delete_transaction(
        db=db, transaction_id=transaction_id, organization_id=organization_id, hard_delete=hard_delete
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Финансовая операция не найдена")
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="delete",
        entity_type="financial_transaction",
        entity_id=str(transaction_id),
        details=f"Удалена финансовая операция #{transaction_id} (hard_delete={hard_delete})",
    )
    return {"status": "success", "message": f"Операция #{transaction_id} успешно удалена"}
