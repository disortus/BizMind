from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
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

        # Get direct offers for this product
        direct_offers = db.query(SupplierOffer).join(Supplier).filter(
            SupplierOffer.product_id == product_id,
            SupplierOffer.is_active == True,
        ).all()

        # Also get global catalog benchmark offers from BizMind base
        global_offers = db.query(SupplierOffer).join(Supplier).filter(
            or_(
                SupplierOffer.organization_id.is_(None),
                Supplier.is_global == True,
                Supplier.source_type == "global",
            ),
            SupplierOffer.is_active == True,
        ).all()

        def _is_product_match(n1: str, n2: str) -> bool:
            if not n1 or not n2:
                return False
            s1 = n1.lower().strip()
            s2 = n2.lower().strip()
            if s1 == s2:
                return True
            if "250" in s1 and "250" in s2 and ("стакан" in s1 or "cup" in s1) and ("стакан" in s2 or "cup" in s2):
                return True
            if "350" in s1 and "350" in s2 and ("стакан" in s1 or "cup" in s1) and ("стакан" in s2 or "cup" in s2):
                return True
            if ("крышк" in s1 or "lid" in s1) and ("крышк" in s2 or "lid" in s2):
                return True
            if ("молок" in s1 or "milk" in s1) and ("молок" in s2 or "milk" in s2):
                return True
            if ("кофе" in s1 or "coffee" in s1 or "зерн" in s1) and ("кофе" in s2 or "coffee" in s2 or "зерн" in s2):
                return True
            if ("сироп" in s1 or "syrup" in s1) and ("карамел" in s1 or "caramel" in s1) and ("карамел" in s2 or "caramel" in s2):
                return True
            if ("сироп" in s1 or "syrup" in s1) and ("орех" in s1 or "hazelnut" in s1) and ("орех" in s2 or "hazelnut" in s2):
                return True
            return False

        # Combine offers, prioritizing org-specific direct offers
        combined_offers_map = {}
        for o in direct_offers:
            combined_offers_map[o.supplier_id] = o

        for go in global_offers:
            if go.supplier_id not in combined_offers_map:
                if go.product_id == product_id or (go.product and _is_product_match(go.product.name, product.name)):
                    combined_offers_map[go.supplier_id] = go

        offers = sorted(combined_offers_map.values(), key=lambda x: x.offered_price)

        offer_items: List[AlternativeOfferItem] = []
        best_offer: Optional[AlternativeOfferItem] = None
        stale_threshold = datetime.utcnow() - timedelta(days=30)

        for o in offers:
            # Price normalization to base product unit (accounting for unit_ratio if set)
            ratio = getattr(product, "unit_ratio", 1.0) or 1.0
            normalized_offered_price = o.offered_price / ratio if ratio > 0 else o.offered_price

            unit_diff = round(current_unit_price - normalized_offered_price, 2)
            tot_diff = round(unit_diff * quantity, 2)
            
            # Delivery impact calculation
            delivery_impact = (o.delivery_cost or 0.0) - current_delivery_cost
            tot_diff_with_delivery = round(tot_diff - delivery_impact, 2)

            # Check staleness
            is_stale = False
            warning_notes = []
            if o.updated_at and o.updated_at < stale_threshold:
                is_stale = True
                warning_notes.append("Предложение получено более 30 дней назад")

            if hasattr(o, "valid_until") and o.valid_until and o.valid_until < datetime.utcnow().date():
                is_stale = True
                warning_notes.append(f"Срок действия цены истек {o.valid_until}")

            if o.minimum_order_quantity and quantity < o.minimum_order_quantity:
                warning_notes.append(
                    f"Количество ({quantity} {o.unit}) меньше минимальной партии ({o.minimum_order_quantity} {o.unit})"
                )

            item = AlternativeOfferItem(
                supplier_id=o.supplier_id,
                supplier_name=o.supplier.name,
                supplier_source_type=getattr(o.supplier, "source_type", "imported") or "imported",
                price_source=getattr(o, "price_source", "catalog") or "catalog",
                is_global_supplier=bool(getattr(o.supplier, "is_global", False)),
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
                is_stale=is_stale,
                warning_note="; ".join(warning_notes) if warning_notes else None,
            )
            offer_items.append(item)

            # Filter for best offer (excluding current supplier if offer belongs to current)
            if unit_diff > 0 and not is_stale and (current_supplier_id is None or o.supplier_id != current_supplier_id):
                if best_offer is None or item.total_difference_with_delivery > best_offer.total_difference_with_delivery:
                    best_offer = item

        formula_note = (
            "Потенциальная экономия = (Текущая цена поставщика − Цена альтернативы) × Количество. "
            "Расчет произведен автоматически на основе сопоставимой единицы измерения. "
            "Обратите внимание: потенциальная экономия не является фактически достигнутой до момента подтверждения закупки."
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
