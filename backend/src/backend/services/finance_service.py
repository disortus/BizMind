from datetime import date, datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.models.models import FinancialTransaction, Product, Purchase
from backend.schemas.schemas import TransactionCreate, FinanceSummary


class FinanceService:
    @staticmethod
    def get_transactions(
        db: Session,
        organization_id: int = 1,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 200,
    ) -> List[FinancialTransaction]:
        query = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id
        )

        if category and category != "Все":
            query = query.filter(FinancialTransaction.category == category)

        if transaction_type and transaction_type != "all":
            query = query.filter(FinancialTransaction.transaction_type == transaction_type)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(FinancialTransaction.description.ilike(search_pattern))

        if start_date:
            query = query.filter(FinancialTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(FinancialTransaction.transaction_date <= end_date)

        return query.order_by(desc(FinancialTransaction.transaction_date), desc(FinancialTransaction.id)).limit(limit).all()

    @staticmethod
    def create_transaction(
        db: Session,
        data: TransactionCreate,
        organization_id: int = 1,
    ) -> FinancialTransaction:
        tx = FinancialTransaction(
            organization_id=organization_id,
            transaction_date=data.transaction_date,
            description=data.description,
            category=data.category,
            amount=abs(data.amount),
            transaction_type=data.transaction_type,
            source=data.source,
            created_at=datetime.utcnow(),
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def get_summary(
        db: Session,
        organization_id: int = 1,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> FinanceSummary:
        query = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id
        )

        if start_date:
            query = query.filter(FinancialTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(FinancialTransaction.transaction_date <= end_date)

        transactions = query.all()

        total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
        total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
        net_profit = total_income - total_expenses

        # Category breakdown
        cat_map: Dict[str, float] = {}
        for t in transactions:
            if t.transaction_type == "expense":
                cat_map[t.category] = cat_map.get(t.category, 0.0) + t.amount

        categories_breakdown = [
            {
                "category": cat,
                "amount": round(amt, 2),
                "percentage": round((amt / total_expenses * 100) if total_expenses > 0 else 0, 1),
            }
            for cat, amt in sorted(cat_map.items(), key=lambda x: x[1], reverse=True)
        ]

        return FinanceSummary(
            total_expenses=round(total_expenses, 2),
            total_income=round(total_income, 2),
            net_profit=round(net_profit, 2),
            period_start=start_date,
            period_end=end_date,
            categories_breakdown=categories_breakdown,
        )

    @staticmethod
    def get_categories(db: Session, organization_id: int = 1) -> List[str]:
        results = db.query(FinancialTransaction.category).filter(
            FinancialTransaction.organization_id == organization_id
        ).distinct().all()
        return [r[0] for r in results if r[0]]
