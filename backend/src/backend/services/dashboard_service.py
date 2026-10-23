from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from backend.models.models import (
    FinancialTransaction,
    Purchase,
    Supplier,
    Product,
    Notification,
    SupplierOffer,
)
from backend.schemas.schemas import (
    DashboardSummary,
    CategoryExpense,
    ExpenseDynamicPoint,
    PurchaseResponse,
    NotificationResponse,
)
from backend.services.comparison_service import ComparisonService


class DashboardService:
    @staticmethod
    def get_dashboard_summary(
        db: Session,
        period: str = "30d",
        organization_id: int = 1,
    ) -> DashboardSummary:
        # Dynamically determine latest activity date or fallback to today
        max_tx_date = db.query(func.max(FinancialTransaction.transaction_date)).filter(
            FinancialTransaction.organization_id == organization_id
        ).scalar()
        max_p_date = db.query(func.max(Purchase.purchase_date)).filter(
            Purchase.organization_id == organization_id
        ).scalar()

        today = max(filter(None, [max_tx_date, max_p_date, date.today()]))

        # Date ranges
        if period == "30d":
            cur_start = today - timedelta(days=30)
            cur_end = today
            prev_start = cur_start - timedelta(days=30)
            prev_end = cur_start
        elif period == "90d":
            cur_start = today - timedelta(days=90)
            cur_end = today
            prev_start = cur_start - timedelta(days=90)
            prev_end = cur_start
        elif period == "month":
            cur_start = date(today.year, today.month, 1)
            cur_end = today
            # Previous month
            prev_month = today.month - 1 if today.month > 1 else 12
            prev_year = today.year if today.month > 1 else today.year - 1
            prev_start = date(prev_year, prev_month, 1)
            prev_end = cur_start - timedelta(days=1)
        else:  # "all"
            cur_start = date(2020, 1, 1)
            cur_end = today + timedelta(days=1)
            prev_start = date(2019, 1, 1)
            prev_end = date(2019, 12, 31)

        # 1. Current period transactions
        current_txs = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id,
            FinancialTransaction.transaction_date >= cur_start,
            FinancialTransaction.transaction_date <= cur_end,
            FinancialTransaction.is_archived == False,
        ).all()

        total_expenses = sum(t.amount for t in current_txs if t.transaction_type == "expense")
        total_income = sum(t.amount for t in current_txs if t.transaction_type == "income")

        # Check if organization is empty (no transactions and no products)
        products_count = db.query(func.count(Product.id)).filter(
            Product.organization_id == organization_id
        ).scalar() or 0
        total_all_txs_count = db.query(func.count(FinancialTransaction.id)).filter(
            FinancialTransaction.organization_id == organization_id
        ).scalar() or 0

        is_empty = (products_count == 0 and total_all_txs_count == 0)
        onboarding_steps = []
        if is_empty:
            onboarding_steps = [
                "1. Добавьте товары в справочник или импортируйте каталог из Excel/CSV",
                "2. Создайте карточки поставщиков и внесите их предложения с ценами",
                "3. Сформируйте первый заказ закупки или зафиксируйте финансовую операцию",
            ]

        # 2. Previous period transactions
        prev_txs = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id,
            FinancialTransaction.transaction_date >= prev_start,
            FinancialTransaction.transaction_date < prev_end,
            FinancialTransaction.is_archived == False,
        ).all()
        previous_period_expenses = sum(t.amount for t in prev_txs if t.transaction_type == "expense")

        if previous_period_expenses > 0:
            expenses_change_percent = round(
                ((total_expenses - previous_period_expenses) / previous_period_expenses) * 100, 1
            )
        else:
            expenses_change_percent = 0.0

        # 3. Categories breakdown
        cat_sums: Dict[str, float] = {}
        for t in current_txs:
            if t.transaction_type == "expense":
                cat_sums[t.category] = cat_sums.get(t.category, 0.0) + t.amount

        categories: List[CategoryExpense] = []
        for cat, amt in sorted(cat_sums.items(), key=lambda x: x[1], reverse=True):
            pct = round((amt / total_expenses * 100) if total_expenses > 0 else 0, 1)
            categories.append(CategoryExpense(category=cat, amount=round(amt, 2), percentage=pct))

        # 4. Dynamics timeline
        dynamics_map: Dict[str, Dict[str, float]] = {}
        for t in sorted(current_txs, key=lambda x: x.transaction_date):
            d_str = t.transaction_date.strftime("%d.%m")
            if d_str not in dynamics_map:
                dynamics_map[d_str] = {"expense": 0.0, "income": 0.0}
            if t.transaction_type == "expense":
                dynamics_map[d_str]["expense"] += t.amount
            else:
                dynamics_map[d_str]["income"] += t.amount

        dynamics = [
            ExpenseDynamicPoint(
                date=k,
                amount=round(v["expense"], 2),
                income=round(v["income"], 2),
            )
            for k, v in dynamics_map.items()
        ]

        # 5. Active suppliers in period
        active_sup_ids = db.query(Purchase.supplier_id).filter(
            Purchase.organization_id == organization_id,
            Purchase.purchase_date >= cur_start,
            Purchase.purchase_date <= cur_end,
        ).distinct().all()
        active_suppliers_count = len(active_sup_ids)

        # 6. Recent purchases (latest 5)
        recent_purchases_raw = db.query(Purchase).join(Product).join(Supplier).filter(
            Purchase.organization_id == organization_id
        ).order_by(desc(Purchase.purchase_date), desc(Purchase.id)).limit(5).all()

        recent_purchases = [
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
            for p in recent_purchases_raw
        ]

        # 7. Unread alerts count & top alerts
        pending_alerts_count = db.query(func.count(Notification.id)).filter(
            Notification.organization_id == organization_id,
            Notification.is_read == False,
        ).scalar() or 0

        top_alerts_raw = db.query(Notification).filter(
            Notification.organization_id == organization_id
        ).order_by(Notification.is_read.asc(), desc(Notification.created_at)).limit(3).all()

        top_price_alerts = [
            NotificationResponse(
                id=n.id,
                title=n.title,
                description=n.description,
                severity=n.severity,
                notification_type=n.notification_type,
                related_product_id=n.related_product_id,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in top_alerts_raw
        ]

        # 8. Potential monthly savings calculation
        potential_savings_monthly = 0.0
        if not is_empty:
            org_products = db.query(Product).filter(
                Product.organization_id == organization_id,
                Product.is_active == True,
            ).all()

            for prod in org_products:
                latest_p = db.query(Purchase).filter(
                    Purchase.product_id == prod.id,
                    Purchase.organization_id == organization_id,
                ).order_by(desc(Purchase.purchase_date), desc(Purchase.id)).first()

                if latest_p:
                    best_offer = db.query(SupplierOffer).filter(
                        SupplierOffer.product_id == prod.id,
                        or_(
                            SupplierOffer.organization_id == organization_id,
                            SupplierOffer.organization_id == None,
                        ),
                        SupplierOffer.supplier_id != latest_p.supplier_id,
                        SupplierOffer.is_active == True,
                    ).order_by(SupplierOffer.offered_price.asc()).first()

                    if best_offer and best_offer.offered_price < latest_p.unit_price:
                        unit_savings = latest_p.unit_price - best_offer.offered_price
                        # Monthly volume estimate from purchases in 90 days or minimum stock
                        qty_90d = db.query(func.sum(Purchase.quantity)).filter(
                            Purchase.product_id == prod.id,
                            Purchase.organization_id == organization_id,
                            Purchase.purchase_date >= today - timedelta(days=90),
                        ).scalar() or 0.0

                        monthly_qty = max(prod.minimum_stock, qty_90d / 3.0)
                        potential_savings_monthly += unit_savings * monthly_qty

        # 9. Featured comparison:
        featured_comp = None
        if not is_empty:
            spike_notif = db.query(Notification).filter(
                Notification.organization_id == organization_id,
                Notification.notification_type == "price_spike",
                Notification.related_product_id != None,
            ).order_by(desc(Notification.created_at)).first()

            target_product_id = None
            target_quantity = 20.0

            if spike_notif and spike_notif.related_product_id:
                target_product_id = spike_notif.related_product_id
                target_prod = db.query(Product).filter(Product.id == target_product_id).first()
                if target_prod and "стакан" in target_prod.name.lower():
                    target_quantity = 60.0
                elif target_prod and "молоко" in target_prod.name.lower():
                    target_quantity = 60.0
                else:
                    target_quantity = 20.0
            else:
                # Intelligent fallback: find a product that has an ACTUAL price spike or ACTUAL cheaper alternative
                org_products = db.query(Product).filter(
                    Product.organization_id == organization_id,
                    Product.is_active == True,
                ).all()

                best_candidate_id = None
                best_candidate_qty = 20.0
                best_candidate_score = -1.0

                for prod in org_products:
                    p_qty = 60.0 if "стакан" in prod.name.lower() or "молоко" in prod.name.lower() else 20.0
                    comp = ComparisonService.compare_product_offers(
                        db=db,
                        product_id=prod.id,
                        quantity=p_qty,
                        organization_id=organization_id,
                    )
                    if not comp:
                        continue

                    # Higher score for actual positive price spikes (> 0%), followed by savings magnitude
                    if comp.price_change_percent and comp.price_change_percent > 0:
                        score = 10000.0 + comp.price_change_percent
                    elif comp.best_offer and comp.best_offer.unit_difference > 0:
                        score = comp.best_offer.total_difference
                    else:
                        score = -1.0

                    if score > best_candidate_score:
                        best_candidate_score = score
                        best_candidate_id = prod.id
                        best_candidate_qty = p_qty

                if best_candidate_id and best_candidate_score > 0:
                    target_product_id = best_candidate_id
                    target_quantity = best_candidate_qty

            if target_product_id:
                featured_comp = ComparisonService.compare_product_offers(
                    db=db,
                    product_id=target_product_id,
                    quantity=target_quantity,
                    organization_id=organization_id,
                )

        return DashboardSummary(
            period=period,
            total_expenses=round(total_expenses, 2),
            previous_period_expenses=round(previous_period_expenses, 2),
            expenses_change_percent=expenses_change_percent,
            total_income=round(total_income, 2),
            active_suppliers_count=active_suppliers_count,
            potential_savings_monthly=round(potential_savings_monthly, 2),
            pending_alerts_count=pending_alerts_count,
            categories=categories,
            dynamics=dynamics,
            recent_purchases=recent_purchases,
            top_price_alerts=top_price_alerts,
            featured_comparison=featured_comp,
            is_empty=is_empty,
            onboarding_steps=onboarding_steps,
        )
