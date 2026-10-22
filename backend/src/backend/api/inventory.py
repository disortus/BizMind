from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response, Body
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import User
from backend.api.deps import get_current_user, require_roles, log_activity
from backend.schemas.schemas import (
    InventoryMovementResponse,
    StockAdjustmentRequest,
)
from backend.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/movements", response_model=List[InventoryMovementResponse])
def get_movements(
    product_id: Optional[int] = Query(None, description="Фильтр по товару"),
    movement_type: Optional[str] = Query(None, description="receipt, write_off, adjustment"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Журнал складских движений с фильтрацией."""
    return InventoryService.get_movements(
        db=db,
        organization_id=current_user.organization_id,
        product_id=product_id,
        movement_type=movement_type,
        limit=limit,
    )


@router.post("/adjust", response_model=InventoryMovementResponse)
def adjust_stock(
    data: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager"])),
):
    """Корректировка остатка по результатам инвентаризации (только Owner/Manager)."""
    res = InventoryService.adjust_stock(
        db=db,
        data=data,
        organization_id=current_user.organization_id,
        user=current_user,
    )
    log_activity(
        db=db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="ADJUST_STOCK",
        entity="InventoryMovement",
        entity_id=res.id,
        details=f"Инвентаризация товара #{data.product_id}: {res.previous_stock} -> {res.resulting_stock} {res.unit} ({data.reason})",
    )
    return res


@router.post("/write-off", response_model=InventoryMovementResponse)
def write_off_stock(
    product_id: int = Body(..., embed=True),
    quantity: float = Body(..., embed=True, gt=0),
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager"])),
):
    """Списание товара со склада (порча, внутреннее использование и т.д.)."""
    res = InventoryService.write_off_stock(
        db=db,
        product_id=product_id,
        quantity=quantity,
        reason=reason,
        organization_id=current_user.organization_id,
        user=current_user,
    )
    log_activity(
        db=db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="WRITE_OFF_STOCK",
        entity="InventoryMovement",
        entity_id=res.id,
        details=f"Списание {quantity} {res.unit} товара #{product_id} ({reason})",
    )
    return res


@router.get("/export")
def export_inventory(
    format: str = Query("xlsx", pattern="^(xlsx|csv|excel)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Экспорт текущих складских остатков в Excel или CSV."""
    normalized_format = "xlsx" if format == "excel" else format
    content = InventoryService.export_inventory(
        db=db,
        organization_id=current_user.organization_id,
        format_type=normalized_format,
    )
    if normalized_format == "csv":
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=inventory_balance.csv"},
        )
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventory_balance.xlsx"},
    )
