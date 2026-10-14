from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.models import Purchase, Product, Supplier
from backend.schemas.schemas import PurchaseResponse, ProductPriceHistoryResponse, PriceHistoryPoint


class PurchaseService:
    @staticmethod
    def get_purchases(
        db: Session,
        organization_id: int = 1,
        product_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 200,
    ) -> List[PurchaseResponse]:
        query = db.query(Purchase).join(Product).join(Supplier).filter(
            Purchase.organization_id == organization_id
        )

        if product_id:
            query = query.filter(Purchase.product_id == product_id)
        if supplier_id:
            query = query.filter(Purchase.supplier_id == supplier_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_pattern)) | (Supplier.name.ilike(search_pattern))
            )

        purchases = query.order_by(desc(Purchase.purchase_date), desc(Purchase.id)).limit(limit).all()

        return [
            PurchaseResponse(
                id=p.id,
                product_id=p.product_id,
                product_name=p.product.name,
                product_category=p.product.category,
                supplier_id=p.supplier_id,
                supplier_name=p.supplier.name,
                purchase_date=p.purchase_date,
                quantity=p.quantity,
                unit=p.unit,
                unit_price=p.unit_price,
                total_price=p.total_price,
                source=p.source,
            )
            for p in purchases
        ]

    @staticmethod
    def get_product_price_history(
        db: Session,
        product_id: int,
        organization_id: int = 1,
    ) -> Optional[ProductPriceHistoryResponse]:
        product = db.query(Product).filter(
            Product.id == product_id, Product.organization_id == organization_id
        ).first()

        if not product:
            return None

        purchases = db.query(Purchase).join(Supplier).filter(
            Purchase.product_id == product_id,
            Purchase.organization_id == organization_id
        ).order_by(Purchase.purchase_date.asc(), Purchase.id.asc()).all()

        if not purchases:
            return ProductPriceHistoryResponse(
                product_id=product.id,
                product_name=product.name,
                unit=product.unit,
                current_price=0.0,
                previous_price=None,
                price_change_percent=None,
                history=[],
            )

        history_points = [
            PriceHistoryPoint(
                date=p.purchase_date,
                price=p.unit_price,
                supplier_name=p.supplier.name,
                quantity=p.quantity,
            )
            for p in purchases
        ]

        current_price = purchases[-1].unit_price
        previous_price = purchases[-2].unit_price if len(purchases) >= 2 else None

        change_percent = None
        if previous_price and previous_price > 0:
            change_percent = round(((current_price - previous_price) / previous_price) * 100, 1)

        return ProductPriceHistoryResponse(
            product_id=product.id,
            product_name=product.name,
            unit=product.unit,
            current_price=current_price,
            previous_price=previous_price,
            price_change_percent=change_percent,
            history=history_points,
        )
