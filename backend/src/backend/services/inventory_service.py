import io
from datetime import datetime
from typing import Optional, List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException
from backend.models.models import InventoryMovement, Product, User
from backend.schemas.schemas import (
    InventoryMovementResponse,
    StockAdjustmentRequest,
)


class InventoryService:
    @staticmethod
    def get_movements(
        db: Session,
        organization_id: int = 1,
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[InventoryMovementResponse]:
        query = db.query(InventoryMovement).join(Product).filter(
            InventoryMovement.organization_id == organization_id
        )
        if product_id:
            query = query.filter(InventoryMovement.product_id == product_id)
        if movement_type and movement_type != "all":
            query = query.filter(InventoryMovement.movement_type == movement_type)

        movements = query.order_by(desc(InventoryMovement.created_at)).limit(limit).all()
        return [
            InventoryMovementResponse(
                id=m.id,
                organization_id=m.organization_id,
                product_id=m.product_id,
                product_name=m.product.name if m.product else "Товар",
                movement_type=m.movement_type,
                quantity=m.quantity,
                unit=m.unit,
                previous_stock=m.previous_stock,
                resulting_stock=m.resulting_stock,
                reason=m.reason,
                reference_id=m.reference_id,
                user_name=m.user.name if m.user else "Система",
                created_at=m.created_at,
            )
            for m in movements
        ]

    @staticmethod
    def adjust_stock(
        db: Session,
        data: StockAdjustmentRequest,
        organization_id: int = 1,
        user: Optional[User] = None,
    ) -> InventoryMovementResponse:
        prod = db.query(Product).filter(
            Product.id == data.product_id,
            Product.organization_id == organization_id,
        ).first()
        if not prod:
            raise HTTPException(status_code=404, detail="Товар не найден")

        prev_stock = prod.current_stock
        new_stock = max(0.0, round(data.actual_stock, 2))
        diff = round(new_stock - prev_stock, 2)
        prod.current_stock = new_stock

        move = InventoryMovement(
            organization_id=organization_id,
            product_id=prod.id,
            movement_type="adjustment",
            quantity=diff,
            unit=prod.unit,
            previous_stock=prev_stock,
            resulting_stock=new_stock,
            reason=data.reason.strip() or "Инвентаризация склада",
            reference_id="MANUAL_ADJUSTMENT",
            user_id=user.id if user else None,
            created_at=datetime.utcnow(),
        )
        db.add(move)
        db.commit()
        db.refresh(move)

        return InventoryMovementResponse(
            id=move.id,
            organization_id=move.organization_id,
            product_id=move.product_id,
            product_name=prod.name,
            movement_type=move.movement_type,
            quantity=move.quantity,
            unit=move.unit,
            previous_stock=move.previous_stock,
            resulting_stock=move.resulting_stock,
            reason=move.reason,
            reference_id=move.reference_id,
            user_name=user.name if user else "Управляющий",
            created_at=move.created_at,
        )

    @staticmethod
    def write_off_stock(
        db: Session,
        product_id: int,
        quantity: float,
        reason: str,
        organization_id: int = 1,
        user: Optional[User] = None,
    ) -> InventoryMovementResponse:
        prod = db.query(Product).filter(
            Product.id == product_id,
            Product.organization_id == organization_id,
        ).first()
        if not prod:
            raise HTTPException(status_code=404, detail="Товар не найден")

        qty = round(abs(quantity), 2)
        prev_stock = prod.current_stock
        new_stock = max(0.0, round(prev_stock - qty, 2))
        prod.current_stock = new_stock

        move = InventoryMovement(
            organization_id=organization_id,
            product_id=prod.id,
            movement_type="write_off",
            quantity=-qty,
            unit=prod.unit,
            previous_stock=prev_stock,
            resulting_stock=new_stock,
            reason=reason.strip() or "Списание сырья/порча",
            reference_id="WRITE_OFF",
            user_id=user.id if user else None,
            created_at=datetime.utcnow(),
        )
        db.add(move)
        db.commit()
        db.refresh(move)

        return InventoryMovementResponse(
            id=move.id,
            organization_id=move.organization_id,
            product_id=move.product_id,
            product_name=prod.name,
            movement_type=move.movement_type,
            quantity=move.quantity,
            unit=move.unit,
            previous_stock=move.previous_stock,
            resulting_stock=move.resulting_stock,
            reason=move.reason,
            reference_id=move.reference_id,
            user_name=user.name if user else "Управляющий",
            created_at=move.created_at,
        )

    @staticmethod
    def export_inventory(
        db: Session,
        organization_id: int = 1,
        format_type: str = "xlsx",
    ) -> bytes:
        products = db.query(Product).filter(
            Product.organization_id == organization_id,
            Product.is_active == True,
        ).order_by(Product.category.asc(), Product.name.asc()).all()

        data = []
        for p in products:
            status_text = "Норма"
            if p.current_stock < p.minimum_stock:
                status_text = "Дефицит"
            elif p.current_stock <= p.minimum_stock * 1.2:
                status_text = "Низкий запас"

            data.append({
                "SKU": p.sku or "-",
                "Наименование": p.name,
                "Категория": p.category,
                "Текущий остаток": p.current_stock,
                "Ед. изм.": p.unit,
                "Минимальный остаток": p.minimum_stock,
                "Статус": status_text,
            })

        df = pd.DataFrame(data)
        out = io.BytesIO()
        if format_type.lower() == "csv":
            df.to_csv(out, index=False, encoding="utf-8-sig")
        else:
            with pd.ExcelWriter(out, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Складские остатки")
        out.seek(0)
        return out.getvalue()
