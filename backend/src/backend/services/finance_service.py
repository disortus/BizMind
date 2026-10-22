import io
from datetime import date, datetime
from typing import Optional, List, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.models.models import FinancialTransaction, Product, Purchase
from backend.schemas.schemas import TransactionCreate, TransactionUpdate, FinanceSummary


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
        include_archived: bool = False,
    ) -> List[FinancialTransaction]:
        query = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id
        )

        if not include_archived:
            query = query.filter(FinancialTransaction.is_archived == False)

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
    def get_transaction_by_id(
        db: Session,
        transaction_id: int,
        organization_id: int = 1,
    ) -> Optional[FinancialTransaction]:
        return db.query(FinancialTransaction).filter(
            FinancialTransaction.id == transaction_id,
            FinancialTransaction.organization_id == organization_id,
        ).first()

    @staticmethod
    def create_transaction(
        db: Session,
        data: TransactionCreate,
        organization_id: int = 1,
    ) -> FinancialTransaction:
        tx = FinancialTransaction(
            organization_id=organization_id,
            transaction_date=data.transaction_date,
            description=data.description.strip(),
            category=data.category.strip(),
            amount=round(abs(data.amount), 2),
            transaction_type=data.transaction_type,
            payment_method=data.payment_method or "cashless",
            source=data.source,
            supplier_id=data.supplier_id,
            purchase_order_id=data.purchase_order_id,
            created_at=datetime.utcnow(),
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def update_transaction(
        db: Session,
        transaction_id: int,
        data: TransactionUpdate,
        organization_id: int = 1,
    ) -> Optional[FinancialTransaction]:
        tx = db.query(FinancialTransaction).filter(
            FinancialTransaction.id == transaction_id,
            FinancialTransaction.organization_id == organization_id,
        ).first()
        if not tx:
            return None

        if data.transaction_date is not None:
            tx.transaction_date = data.transaction_date
        if data.description is not None:
            tx.description = data.description.strip()
        if data.category is not None:
            tx.category = data.category.strip()
        if data.amount is not None:
            tx.amount = round(abs(data.amount), 2)
        if data.transaction_type is not None:
            tx.transaction_type = data.transaction_type
        if data.payment_method is not None:
            tx.payment_method = data.payment_method
        if data.supplier_id is not None:
            tx.supplier_id = data.supplier_id

        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def delete_transaction(
        db: Session,
        transaction_id: int,
        organization_id: int = 1,
        hard_delete: bool = False,
    ) -> bool:
        tx = db.query(FinancialTransaction).filter(
            FinancialTransaction.id == transaction_id,
            FinancialTransaction.organization_id == organization_id,
        ).first()
        if not tx:
            return False

        if hard_delete:
            db.delete(tx)
        else:
            tx.is_archived = True

        db.commit()
        return True

    @staticmethod
    def get_summary(
        db: Session,
        organization_id: int = 1,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> FinanceSummary:
        query = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id,
            FinancialTransaction.is_archived == False,
        )

        if start_date:
            query = query.filter(FinancialTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(FinancialTransaction.transaction_date <= end_date)

        transactions = query.all()

        total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
        total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
        net_profit = total_income - total_expenses

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
        results = (
            db.query(FinancialTransaction.category)
            .filter(
                FinancialTransaction.organization_id == organization_id,
                FinancialTransaction.is_archived == False,
            )
            .distinct()
            .order_by(FinancialTransaction.category.asc())
            .all()
        )
        return [r[0] for r in results if r[0]]

    @staticmethod
    def export_transactions(
        db: Session,
        organization_id: int = 1,
        format_type: str = "xlsx",
    ) -> bytes:
        transactions = db.query(FinancialTransaction).filter(
            FinancialTransaction.organization_id == organization_id,
            FinancialTransaction.is_archived == False,
        ).order_by(desc(FinancialTransaction.transaction_date)).all()

        data = []
        for t in transactions:
            data.append({
                "ID": t.id,
                "Дата": t.transaction_date.strftime("%Y-%m-%d"),
                "Описание": t.description,
                "Категория": t.category,
                "Тип": "Доход" if t.transaction_type == "income" else "Расход",
                "Способ оплаты": t.payment_method or "Безналичный",
                "Сумма (₸)": t.amount,
                "Источник": t.source,
            })

        df = pd.DataFrame(data)
        out = io.BytesIO()
        if format_type.lower() == "csv":
            df.to_csv(out, index=False, encoding="utf-8-sig")
        else:
            with pd.ExcelWriter(out, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Финансы")
        out.seek(0)
        return out.getvalue()
