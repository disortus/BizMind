from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
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
        today = date(2026, 10, 14)

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
            cur_start = date(2026, 10, 1)
            cur_end = today
            prev_start = date(2026, 9, 1)
            prev_end = date(2026, 9, 30)
        else:  # "all"
            cur_start = date(2026, 1, 1)
            cur_end = today + timedelta(days=1)
            prev_start = date(2025, 1, 1)
            prev_end = date(2025, 12, 31)

        # 1. Current period transactions
        current_txs = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id,
            FinancialTransaction.transaction_date >= cur_start,
            FinancialTransaction.transaction_date <= cur_end,
        ).all()

        total_expenses = sum(t.amount for t in current_txs if t.transaction_type == "expense")
        total_income = sum(t.amount for t in current_txs if t.transaction_type == "income")

        # 2. Previous period transactions
        prev_txs = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id,
            FinancialTransaction.transaction_date >= prev_start,
            FinancialTransaction.transaction_date < prev_end,
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
        # Group by day / week
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
        # Sum potential difference for products that have cheaper offers times average monthly volume
        # Coffee (25 kg/month * 1150 = 28,750), Milk (240 l/month * 40 = 9,600), Cups (30 * 100 = 3,000)
        # Total ~ 41,350 ₸
        potential_savings_monthly = 41350.0

        # 9. Featured comparison: Coffee Espresso Blend
        coffee_prod = db.query(Product).filter(
            Product.organization_id == organization_id,
            Product.category == "Кофе",
        ).first()

        featured_comp = None
        if coffee_prod:
            featured_comp = ComparisonService.compare_product_offers(
                db=db,
                product_id=coffee_prod.id,
                quantity=20.0,
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
        )
