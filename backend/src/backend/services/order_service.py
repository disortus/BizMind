from datetime import date, datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status
from backend.models.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Product,
    Supplier,
    InventoryMovement,
    FinancialTransaction,
    Purchase,
    User,
)
from backend.schemas.schemas import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderReceiveRequest,
    PurchaseOrderResponse,
    PurchaseOrderItemResponse,
)


class OrderService:
    @staticmethod
    def get_orders(
        db: Session,
        organization_id: int = 1,
        status_filter: Optional[str] = None,
        supplier_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[PurchaseOrderResponse]:
        query = db.query(PurchaseOrder).filter(PurchaseOrder.organization_id == organization_id)
        if status_filter and status_filter != "all":
            query = query.filter(PurchaseOrder.status == status_filter)
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)

        orders = query.order_by(desc(PurchaseOrder.order_date), desc(PurchaseOrder.id)).limit(limit).all()
        return [OrderService._to_response(o) for o in orders]

    @staticmethod
    def get_order_by_id(
        db: Session,
        order_id: int,
        organization_id: int = 1,
    ) -> Optional[PurchaseOrderResponse]:
        order = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == order_id,
            PurchaseOrder.organization_id == organization_id,
        ).first()
        if not order:
            return None
        return OrderService._to_response(order)

    @staticmethod
    def create_order(
        db: Session,
        data: PurchaseOrderCreate,
        organization_id: int = 1,
        user: Optional[User] = None,
    ) -> PurchaseOrderResponse:
        supplier = db.query(Supplier).filter(
            Supplier.id == data.supplier_id,
            Supplier.organization_id == organization_id,
        ).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Поставщик не найден")

        if not data.items:
            raise HTTPException(status_code=400, detail="Заказ должен содержать хотя бы одну товарную позицию")

        # Generate unique order number
        count_existing = db.query(func.count(PurchaseOrder.id)).filter(
            PurchaseOrder.organization_id == organization_id
        ).scalar() or 0
        year = data.order_date.year
        order_num = f"PO-{year}-{(count_existing + 1):04d}"

        subtotal = 0.0
        order_items_to_create = []

        for it in data.items:
            prod = db.query(Product).filter(
                Product.id == it.product_id,
                Product.organization_id == organization_id,
            ).first()
            if not prod:
                raise HTTPException(status_code=404, detail=f"Товар ID {it.product_id} не найден")

            qty = round(abs(it.ordered_quantity), 2)
            price = round(abs(it.unit_price), 2)
            tot = round(qty * price, 2)
            subtotal += tot

            order_items_to_create.append(
                PurchaseOrderItem(
                    product_id=prod.id,
                    ordered_quantity=qty,
                    received_quantity=None,
                    unit=it.unit or prod.unit,
                    unit_price=price,
                    total_price=tot,
                )
            )

        delivery = max(0.0, data.delivery_cost)
        total = round(subtotal + delivery, 2)

        order = PurchaseOrder(
            organization_id=organization_id,
            order_number=order_num,
            supplier_id=supplier.id,
            order_date=data.order_date,
            status="draft",
            subtotal_amount=round(subtotal, 2),
            delivery_cost=round(delivery, 2),
            total_amount=total,
            notes=data.notes.strip() if data.notes else None,
            created_by_user_id=user.id if user else None,
            created_at=datetime.utcnow(),
            items=order_items_to_create,
        )

        db.add(order)
        db.commit()
        db.refresh(order)
        return OrderService._to_response(order)

    @staticmethod
    def update_order(
        db: Session,
        order_id: int,
        data: PurchaseOrderUpdate,
        organization_id: int = 1,
    ) -> PurchaseOrderResponse:
        order = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == order_id,
            PurchaseOrder.organization_id == organization_id,
        ).first()
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        if data.status:
            target_status = data.status.lower()
            if order.status == "received":
                raise HTTPException(status_code=400, detail="Нельзя изменить статус уже принятого заказа")
            if order.status == "cancelled":
                raise HTTPException(status_code=400, detail="Нельзя изменить статус отмененного заказа")

            if target_status in ["draft", "confirmed", "cancelled"]:
                order.status = target_status
            else:
                raise HTTPException(status_code=400, detail=f"Недопустимый статус: {data.status}")

        if data.delivery_cost is not None:
            order.delivery_cost = max(0.0, data.delivery_cost)
            order.total_amount = round(order.subtotal_amount + order.delivery_cost, 2)

        if data.notes is not None:
            order.notes = data.notes.strip()

        db.commit()
        db.refresh(order)
        return OrderService._to_response(order)

    @staticmethod
    def receive_order(
        db: Session,
        order_id: int,
        data: PurchaseOrderReceiveRequest,
        organization_id: int = 1,
        user: Optional[User] = None,
    ) -> PurchaseOrderResponse:
        order = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == order_id,
            PurchaseOrder.organization_id == organization_id,
        ).first()
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        if order.status == "received":
            raise HTTPException(status_code=400, detail="Заказ уже был принят ранее. Повторная приемка запрещена.")
        if order.status == "cancelled":
            raise HTTPException(status_code=400, detail="Нельзя принять отмененный заказ")

        now = datetime.utcnow()
        order.received_at = now
        order.status = "received"

        # Update each item and create inventory movement
        for item in order.items:
            actual_qty = item.ordered_quantity
            if data.received_quantities and item.id in data.received_quantities:
                actual_qty = max(0.0, float(data.received_quantities[item.id]))
            item.received_quantity = actual_qty

            prod = item.product
            prev_stock = prod.current_stock
            new_stock = round(prev_stock + actual_qty, 2)
            prod.current_stock = new_stock

            movement = InventoryMovement(
                organization_id=organization_id,
                product_id=prod.id,
                movement_type="receipt",
                quantity=actual_qty,
                unit=item.unit,
                previous_stock=prev_stock,
                resulting_stock=new_stock,
                reason=f"Поступление по заказу {order.order_number}",
                reference_id=order.order_number,
                user_id=user.id if user else None,
                created_at=now,
            )
            db.add(movement)

            # Record in legacy Purchase table for analytical and price-spike continuity
            legacy_p = Purchase(
                organization_id=organization_id,
                product_id=prod.id,
                supplier_id=order.supplier_id,
                purchase_date=order.order_date,
                quantity=actual_qty,
                unit=item.unit,
                unit_price=item.unit_price,
                total_price=round(actual_qty * item.unit_price, 2),
                source="purchase_order",
                purchase_order_id=order.id,
                created_at=now,
            )
            db.add(legacy_p)

        # Optionally record financial expense linked to this purchase order
        if data.record_financial_expense:
            first_cat = order.items[0].product.category if order.items else "Закупка сырья"
            tx = FinancialTransaction(
                organization_id=organization_id,
                transaction_date=order.order_date,
                description=f"Оплата поставки {order.order_number} ({order.supplier.name})",
                category=f"Закупка: {first_cat}",
                amount=order.total_amount,
                transaction_type="expense",
                payment_method=data.payment_method or "cashless",
                source="purchase_order",
                supplier_id=order.supplier_id,
                purchase_order_id=order.id,
                created_at=now,
            )
            db.add(tx)

        db.commit()
        db.refresh(order)
        return OrderService._to_response(order)

    @staticmethod
    def _to_response(o: PurchaseOrder) -> PurchaseOrderResponse:
        items_resp = [
            PurchaseOrderItemResponse(
                id=it.id,
                purchase_order_id=it.purchase_order_id,
                product_id=it.product_id,
                product_name=it.product.name if it.product else "Товар",
                ordered_quantity=it.ordered_quantity,
                received_quantity=it.received_quantity,
                unit=it.unit,
                unit_price=it.unit_price,
                total_price=it.total_price,
            )
            for it in o.items
        ]
        return PurchaseOrderResponse(
            id=o.id,
            organization_id=o.organization_id,
            order_number=o.order_number,
            supplier_id=o.supplier_id,
            supplier_name=o.supplier.name if o.supplier else "Поставщик",
            order_date=o.order_date,
            status=o.status,
            subtotal_amount=o.subtotal_amount,
            delivery_cost=o.delivery_cost,
            total_amount=o.total_amount,
            notes=o.notes,
            created_by_name=o.created_by_user.name if o.created_by_user else None,
            received_at=o.received_at,
            created_at=o.created_at,
            items=items_resp,
        )
