from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.models import Product, Supplier, Purchase, SupplierOffer
from backend.schemas.schemas import PriceComparisonResponse, AlternativeOfferItem


class ComparisonService:
    @staticmethod
    def compare_product_offers(
        db: Session,
        product_id: int,
        quantity: float = 20.0,
        organization_id: int = 1,
    ) -> Optional[PriceComparisonResponse]:
        product = db.query(Product).filter(
            Product.id == product_id, Product.organization_id == organization_id
        ).first()

        if not product:
            return None

        # Find latest purchase to determine current supplier and unit price
        latest_purchases = db.query(Purchase).filter(
            Purchase.product_id == product_id,
            Purchase.organization_id == organization_id
        ).order_by(desc(Purchase.purchase_date), desc(Purchase.id)).limit(2).all()

        current_supplier_id = None
        current_supplier_name = None
        current_unit_price = 0.0
        previous_unit_price = None
        price_change_percent = None
        current_delivery_cost = 0.0

        if latest_purchases:
            latest = latest_purchases[0]
            current_supplier_id = latest.supplier_id
            current_supplier_name = latest.supplier.name
            current_unit_price = latest.unit_price
            current_delivery_cost = latest.supplier.delivery_cost or 0.0

            if len(latest_purchases) > 1:
                prev = latest_purchases[1]
                previous_unit_price = prev.unit_price
                if previous_unit_price > 0:
                    price_change_percent = round(
                        ((current_unit_price - previous_unit_price) / previous_unit_price) * 100, 1
                    )

        # Get offers
        offers = db.query(SupplierOffer).join(Supplier).filter(
            SupplierOffer.product_id == product_id,
            SupplierOffer.organization_id == organization_id
        ).order_by(SupplierOffer.offered_price.asc()).all()

        offer_items: List[AlternativeOfferItem] = []
        best_offer: Optional[AlternativeOfferItem] = None

        for o in offers:
            unit_diff = round(current_unit_price - o.offered_price, 2)
            tot_diff = round(unit_diff * quantity, 2)
            
            # Delivery impact calculation
            delivery_impact = (o.delivery_cost or 0.0) - current_delivery_cost
            tot_diff_with_delivery = round(tot_diff - delivery_impact, 2)

            item = AlternativeOfferItem(
                supplier_id=o.supplier_id,
                supplier_name=o.supplier.name,
                offered_price=o.offered_price,
                unit=o.unit,
                package_quantity=o.package_quantity,
                minimum_order_quantity=o.minimum_order_quantity,
                delivery_cost=o.delivery_cost or 0.0,
                unit_difference=unit_diff,
                total_difference=tot_diff,
                total_difference_with_delivery=tot_diff_with_delivery,
                updated_at=o.updated_at,
                is_better=unit_diff > 0,
                is_demo=o.is_demo,
            )
            offer_items.append(item)

            # Filter for best offer (excluding current supplier if offer belongs to current)
            if unit_diff > 0:
                if best_offer is None or item.total_difference > best_offer.total_difference:
                    best_offer = item

        formula_note = (
            "Потенциальная разница = (Текущая цена поставщика − Цена альтернативы) × Количество. "
            "Расчет произведен программно на основе сопоставимой единицы измерения. "
            "Условия минимального заказа и доставки учитываются при итоговом согласовании."
        )

        return PriceComparisonResponse(
            product_id=product.id,
            product_name=product.name,
            unit=product.unit,
            current_supplier_id=current_supplier_id,
            current_supplier_name=current_supplier_name,
            current_unit_price=current_unit_price,
            previous_unit_price=previous_unit_price,
            price_change_percent=price_change_percent,
            selected_quantity=quantity,
            alternative_offers=offer_items,
            best_offer=best_offer,
            formula_note=formula_note,
        )
