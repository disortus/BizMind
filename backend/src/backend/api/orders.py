from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id, get_current_user, require_roles, log_activity
from backend.models.models import User
from backend.schemas.schemas import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderReceiveRequest,
    PurchaseOrderResponse,
)
from backend.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=List[PurchaseOrderResponse])
def get_orders(
    status: Optional[str] = None,
    supplier_id: Optional[int] = None,
    limit: int = Query(100, le=200),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return OrderService.get_orders(
        db=db,
        organization_id=organization_id,
        status_filter=status,
        supplier_id=supplier_id,
        limit=limit,
    )


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
def get_order(
    order_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    order = OrderService.get_order_by_id(db=db, order_id=order_id, organization_id=organization_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return order


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: PurchaseOrderCreate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager", "employee"])),
    db: Session = Depends(get_db),
):
    order = OrderService.create_order(
        db=db, data=data, organization_id=organization_id, user=user
    )
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="create_order",
        entity_type="purchase_order",
        entity_id=str(order.id),
        details=f"Сформирован заказ {order.order_number} ({order.supplier_name}) на сумму {order.total_amount} ₸",
    )
    return order


@router.put("/{order_id}", response_model=PurchaseOrderResponse)
def update_order(
    order_id: int,
    data: PurchaseOrderUpdate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    order = OrderService.update_order(
        db=db, order_id=order_id, data=data, organization_id=organization_id
    )
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="update_order",
        entity_type="purchase_order",
        entity_id=str(order.id),
        details=f"Обновлен статус заказа {order.order_number}: {order.status}",
    )
    return order


@router.post("/{order_id}/receive", response_model=PurchaseOrderResponse)
def receive_order(
    order_id: int,
    data: PurchaseOrderReceiveRequest,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    order = OrderService.receive_order(
        db=db, order_id=order_id, data=data, organization_id=organization_id, user=user
    )
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="receive_order",
        entity_type="purchase_order",
        entity_id=str(order.id),
        details=f"Принят заказ {order.order_number} ({order.supplier_name}) на сумму {order.total_amount} ₸. Остатки обновлены.",
    )
    return order


@router.get("/{order_id}/document", response_class=PlainTextResponse)
def get_order_document(
    order_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    order = OrderService.get_order_by_id(db=db, order_id=order_id, organization_id=organization_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    lines = [
        "=" * 60,
        f"           БЛАНК ЗАКАЗА НА ЗАКУПКУ: {order.order_number}",
        "=" * 60,
        f"Дата заказа: {order.order_date}",
        f"Поставщик:   {order.supplier_name}",
        f"Статус:      {order.status.upper()}",
        f"Создал:      {order.created_by_name or 'Управляющий'}",
        "-" * 60,
        f"{'№':<3} {'Товар':<30} {'Кол-во':<10} {'Цена (₸)':<10} {'Сумма (₸)':<10}",
        "-" * 60,
    ]
    for i, it in enumerate(order.items, 1):
        lines.append(
            f"{i:<3} {it.product_name[:28]:<30} {it.ordered_quantity} {it.unit:<5} {it.unit_price:>8.1f} {it.total_price:>9.1f}"
        )
    lines.extend([
        "-" * 60,
        f"Подытог:                                    {order.subtotal_amount:>10.2f} ₸",
        f"Доставка:                                   {order.delivery_cost:>10.2f} ₸",
        f"ИТОГО К ОПЛАТЕ:                             {order.total_amount:>10.2f} ₸",
        "=" * 60,
        f"Примечание: {order.notes or 'Без примечаний'}",
        "=" * 60,
    ])
    return "\n".join(lines)
