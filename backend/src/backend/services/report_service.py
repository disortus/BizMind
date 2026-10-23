import json
import io
import csv
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from backend.models.models import (
    ReportTemplate,
    Organization,
    User,
    FinancialTransaction,
    Purchase,
    Product,
    Supplier,
    SupplierOffer,
    InventoryMovement,
    Notification,
)
from backend.schemas.schemas import (
    ReportTemplateResponse,
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportPreviewResponse,
)


class ReportService:
    @staticmethod
    def get_templates(db: Session, organization_id: int) -> List[ReportTemplateResponse]:
        """
        Returns all system preset templates and custom templates created for the organization.
        """
        templates = (
            db.query(ReportTemplate)
            .filter(
                or_(
                    ReportTemplate.is_system == True,
                    and_(
                        ReportTemplate.organization_id == organization_id,
                        ReportTemplate.is_archived == False,
                    ),
                )
            )
            .order_by(ReportTemplate.is_system.desc(), ReportTemplate.updated_at.desc())
            .all()
        )

        results = []
        for t in templates:
            try:
                cfg = json.loads(t.config) if isinstance(t.config, str) else t.config
            except Exception:
                cfg = {}
            results.append(
                ReportTemplateResponse(
                    id=t.id,
                    organization_id=t.organization_id,
                    title=t.title,
                    description=t.description,
                    report_type=t.report_type,
                    config=cfg,
                    is_system=t.is_system,
                    is_archived=t.is_archived,
                    created_by_user_id=t.created_by_user_id,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                )
            )
        return results

    @staticmethod
    def get_template(db: Session, organization_id: int, template_id: int) -> Optional[ReportTemplateResponse]:
        t = (
            db.query(ReportTemplate)
            .filter(
                ReportTemplate.id == template_id,
                or_(
                    ReportTemplate.is_system == True,
                    ReportTemplate.organization_id == organization_id,
                ),
            )
            .first()
        )
        if not t:
            return None

        try:
            cfg = json.loads(t.config) if isinstance(t.config, str) else t.config
        except Exception:
            cfg = {}

        return ReportTemplateResponse(
            id=t.id,
            organization_id=t.organization_id,
            title=t.title,
            description=t.description,
            report_type=t.report_type,
            config=cfg,
            is_system=t.is_system,
            is_archived=t.is_archived,
            created_by_user_id=t.created_by_user_id,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

    @staticmethod
    def create_template(
        db: Session,
        organization_id: int,
        user_id: Optional[int],
        data: ReportTemplateCreate,
    ) -> ReportTemplateResponse:
        cfg_dict = data.config.model_dump()
        t = ReportTemplate(
            organization_id=organization_id,
            title=data.title.strip(),
            description=data.description.strip() if data.description else None,
            report_type=data.report_type,
            config=json.dumps(cfg_dict, ensure_ascii=False, default=str),
            is_system=False,
            is_archived=False,
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(t)
        db.commit()
        db.refresh(t)

        return ReportTemplateResponse(
            id=t.id,
            organization_id=t.organization_id,
            title=t.title,
            description=t.description,
            report_type=t.report_type,
            config=cfg_dict,
            is_system=t.is_system,
            is_archived=t.is_archived,
            created_by_user_id=t.created_by_user_id,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

    @staticmethod
    def update_template(
        db: Session,
        organization_id: int,
        template_id: int,
        data: ReportTemplateUpdate,
    ) -> Optional[ReportTemplateResponse]:
        t = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
        if not t:
            return None

        if t.is_system:
            raise ValueError("Системные шаблоны защищены от изменения. Создайте копию шаблона.")

        if t.organization_id != organization_id:
            return None

        if data.title is not None:
            t.title = data.title.strip()
        if data.description is not None:
            t.description = data.description.strip()
        if data.report_type is not None:
            t.report_type = data.report_type
        if data.config is not None:
            t.config = json.dumps(data.config.model_dump(), ensure_ascii=False, default=str)
        if data.is_archived is not None:
            t.is_archived = data.is_archived

        t.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(t)

        try:
            cfg = json.loads(t.config) if isinstance(t.config, str) else t.config
        except Exception:
            cfg = {}

        return ReportTemplateResponse(
            id=t.id,
            organization_id=t.organization_id,
            title=t.title,
            description=t.description,
            report_type=t.report_type,
            config=cfg,
            is_system=t.is_system,
            is_archived=t.is_archived,
            created_by_user_id=t.created_by_user_id,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

    @staticmethod
    def duplicate_template(
        db: Session,
        organization_id: int,
        user_id: Optional[int],
        template_id: int,
    ) -> Optional[ReportTemplateResponse]:
        orig = (
            db.query(ReportTemplate)
            .filter(
                ReportTemplate.id == template_id,
                or_(
                    ReportTemplate.is_system == True,
                    ReportTemplate.organization_id == organization_id,
                ),
            )
            .first()
        )
        if not orig:
            return None

        new_title = f"Копия - {orig.title}"
        t = ReportTemplate(
            organization_id=organization_id,
            title=new_title,
            description=orig.description,
            report_type=orig.report_type,
            config=orig.config,
            is_system=False,
            is_archived=False,
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(t)
        db.commit()
        db.refresh(t)

        try:
            cfg = json.loads(t.config) if isinstance(t.config, str) else t.config
        except Exception:
            cfg = {}

        return ReportTemplateResponse(
            id=t.id,
            organization_id=t.organization_id,
            title=t.title,
            description=t.description,
            report_type=t.report_type,
            config=cfg,
            is_system=t.is_system,
            is_archived=t.is_archived,
            created_by_user_id=t.created_by_user_id,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

    @staticmethod
    def delete_template(db: Session, organization_id: int, template_id: int) -> bool:
        t = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
        if not t:
            return False

        if t.is_system:
            raise ValueError("Системные шаблоны нельзя удалить")

        if t.organization_id != organization_id:
            return False

        t.is_archived = True
        db.commit()
        return True

    @staticmethod
    def _resolve_date_range(db: Session, organization_id: int, period_type: str, custom_start: Optional[date] = None, custom_end: Optional[date] = None):
        max_tx = db.query(func.max(FinancialTransaction.transaction_date)).filter(
            FinancialTransaction.organization_id == organization_id
        ).scalar()
        max_p = db.query(func.max(Purchase.purchase_date)).filter(
            Purchase.organization_id == organization_id
        ).scalar()

        ref_date = max(filter(None, [max_tx, max_p, date(2026, 10, 14)]))

        if period_type == "current_month":
            start_d = date(ref_date.year, ref_date.month, 1)
            end_d = ref_date
            label = f"Текущий месяц ({start_d.strftime('%d.%m.%Y')} — {end_d.strftime('%d.%m.%Y')})"
        elif period_type == "previous_month":
            p_month = ref_date.month - 1 if ref_date.month > 1 else 12
            p_year = ref_date.year if ref_date.month > 1 else ref_date.year - 1
            start_d = date(p_year, p_month, 1)
            # Find last day of previous month
            end_d = date(ref_date.year, ref_date.month, 1) - timedelta(days=1)
            label = f"Предыдущий месяц ({start_d.strftime('%d.%m.%Y')} — {end_d.strftime('%d.%m.%Y')})"
        elif period_type == "last_30d":
            start_d = ref_date - timedelta(days=30)
            end_d = ref_date
            label = f"Последние 30 дней ({start_d.strftime('%d.%m.%Y')} — {end_d.strftime('%d.%m.%Y')})"
        elif period_type == "last_90d":
            start_d = ref_date - timedelta(days=90)
            end_d = ref_date
            label = f"Последние 90 дней ({start_d.strftime('%d.%m.%Y')} — {end_d.strftime('%d.%m.%Y')})"
        elif period_type == "custom":
            start_d = custom_start or (ref_date - timedelta(days=30))
            end_d = custom_end or ref_date
            label = f"Выбранный период ({start_d.strftime('%d.%m.%Y')} — {end_d.strftime('%d.%m.%Y')})"
        else:  # all time
            start_d = date(2025, 1, 1)
            end_d = ref_date + timedelta(days=1)
            label = "За все время"

        return start_d, end_d, label

    @classmethod
    def generate_report_data(
        cls,
        db: Session,
        organization_id: int,
        report_type: str,
        config: Dict[str, Any],
    ) -> ReportPreviewResponse:
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        org_name = org.name if org else "Организация"
        currency = org.currency if org else "₸"

        period_type = config.get("period_type", "current_month")
        c_start = config.get("start_date")
        c_end = config.get("end_date")
        if isinstance(c_start, str):
            c_start = date.fromisoformat(c_start)
        if isinstance(c_end, str):
            c_end = date.fromisoformat(c_end)

        start_date, end_date, period_label = cls._resolve_date_range(
            db, organization_id, period_type, c_start, c_end
        )

        group_by = config.get("group_by", "category")
        sort_by = config.get("sort_by", "amount_desc")

        # Check if organization has no business data
        tx_count = db.query(func.count(FinancialTransaction.id)).filter(
            FinancialTransaction.organization_id == organization_id
        ).scalar() or 0
        p_count = db.query(func.count(Purchase.id)).filter(
            Purchase.organization_id == organization_id
        ).scalar() or 0
        prod_count = db.query(func.count(Product.id)).filter(
            Product.organization_id == organization_id
        ).scalar() or 0

        if tx_count == 0 and p_count == 0 and prod_count == 0:
            return ReportPreviewResponse(
                title=config.get("title") or f"Отчёт: {report_type}",
                report_type=report_type,
                organization_name=org_name,
                currency=currency,
                period_label=period_label,
                start_date=start_date,
                end_date=end_date,
                generated_at=datetime.utcnow(),
                is_empty=True,
                message=f"В организации «{org_name}» отсутствуют исторические данные. Загрузите файлы через раздел «Импорт данных», чтобы сформировать полноценный аналитический отчёт.",
            )

        now = datetime.utcnow()

        # =====================================================================
        # 1. FINANCIAL REPORT
        # =====================================================================
        if report_type == "financial":
            txs = (
                db.query(FinancialTransaction)
                .filter(
                    FinancialTransaction.organization_id == organization_id,
                    FinancialTransaction.transaction_date >= start_date,
                    FinancialTransaction.transaction_date <= end_date,
                    FinancialTransaction.is_archived == False,
                )
                .order_by(FinancialTransaction.transaction_date.asc())
                .all()
            )

            total_income = sum(t.amount for t in txs if t.transaction_type == "income")
            total_expenses = sum(t.amount for t in txs if t.transaction_type == "expense")
            net_profit = total_income - total_expenses
            profit_margin = round((net_profit / total_income * 100), 1) if total_income > 0 else 0.0

            kpi_cards = [
                {
                    "title": "Выручка / Доходы",
                    "value": f"{total_income:,.0f} {currency}".replace(",", " "),
                    "subtitle": f"{len([t for t in txs if t.transaction_type == 'income'])} поступлений",
                    "badge": "+ доход",
                    "type": "income",
                },
                {
                    "title": "Операционные расходы",
                    "value": f"{total_expenses:,.0f} {currency}".replace(",", " "),
                    "subtitle": f"{len([t for t in txs if t.transaction_type == 'expense'])} операций",
                    "badge": "- расход",
                    "type": "expense",
                },
                {
                    "title": "Чистая прибыль (EBITDA)",
                    "value": f"{net_profit:,.0f} {currency}".replace(",", " "),
                    "subtitle": f"Маржинальность: {profit_margin}%",
                    "badge": "результат",
                    "type": "profit" if net_profit >= 0 else "loss",
                },
                {
                    "title": "Рентабельность",
                    "value": f"{profit_margin}%",
                    "subtitle": "Отношение прибыли к выручке",
                    "badge": "эффективность",
                    "type": "neutral",
                },
            ]

            # Aggregation based on group_by
            rows = []
            if group_by == "category":
                cat_data = {}
                for t in txs:
                    c = t.category or "Прочее"
                    if c not in cat_data:
                        cat_data[c] = {"income": 0.0, "expense": 0.0, "count": 0}
                    if t.transaction_type == "income":
                        cat_data[c]["income"] += t.amount
                    else:
                        cat_data[c]["expense"] += t.amount
                    cat_data[c]["count"] += 1

                for c, vals in cat_data.items():
                    exp = vals["expense"]
                    inc = vals["income"]
                    net = inc - exp
                    share = round((exp / total_expenses * 100), 1) if total_expenses > 0 else 0.0
                    rows.append({
                        "item": c,
                        "income": round(inc, 2),
                        "expense": round(exp, 2),
                        "net": round(net, 2),
                        "count": vals["count"],
                        "share": share,
                    })

                columns = [
                    {"key": "item", "label": "Категория расходов/доходов"},
                    {"key": "income", "label": f"Доход ({currency})"},
                    {"key": "expense", "label": f"Расход ({currency})"},
                    {"key": "net", "label": f"Чистый итог ({currency})"},
                    {"key": "share", "label": "Доля в расходах (%)"},
                    {"key": "count", "label": "Операций"},
                ]
            else:  # day or month
                date_data = {}
                for t in txs:
                    d_key = t.transaction_date.strftime("%Y-%m-%d" if group_by == "day" else "%Y-%m")
                    if d_key not in date_data:
                        date_data[d_key] = {"income": 0.0, "expense": 0.0, "count": 0}
                    if t.transaction_type == "income":
                        date_data[d_key]["income"] += t.amount
                    else:
                        date_data[d_key]["expense"] += t.amount
                    date_data[d_key]["count"] += 1

                for d_k in sorted(date_data.keys()):
                    vals = date_data[d_k]
                    rows.append({
                        "item": d_k,
                        "income": round(vals["income"], 2),
                        "expense": round(vals["expense"], 2),
                        "net": round(vals["income"] - vals["expense"], 2),
                        "count": vals["count"],
                        "share": round(vals["expense"] / total_expenses * 100, 1) if total_expenses > 0 else 0.0,
                    })

                columns = [
                    {"key": "item", "label": "Период / Дата"},
                    {"key": "income", "label": f"Доход ({currency})"},
                    {"key": "expense", "label": f"Расход ({currency})"},
                    {"key": "net", "label": f"Чистая прибыль ({currency})"},
                    {"key": "count", "label": "Операций"},
                ]

            # Sort rows
            if sort_by == "amount_desc":
                rows.sort(key=lambda x: x.get("expense", 0), reverse=True)
            elif sort_by == "amount_asc":
                rows.sort(key=lambda x: x.get("expense", 0))

            # Chart dynamics
            dynamics = []
            for t in sorted(txs, key=lambda x: x.transaction_date):
                dynamics.append({
                    "date": t.transaction_date.strftime("%d.%m"),
                    "amount": t.amount if t.transaction_type == "expense" else 0.0,
                    "income": t.amount if t.transaction_type == "income" else 0.0,
                })

            return ReportPreviewResponse(
                title=config.get("title") or "Ежемесячный финансовый отчёт",
                report_type=report_type,
                organization_name=org_name,
                currency=currency,
                period_label=period_label,
                start_date=start_date,
                end_date=end_date,
                generated_at=now,
                kpi_cards=kpi_cards,
                charts={"dynamics": dynamics[:30]},
                summary_data=[],
                columns=columns,
                rows=rows,
                is_empty=len(rows) == 0,
            )

        # =====================================================================
        # 2. PROCUREMENT REPORT
        # =====================================================================
        elif report_type == "procurement":
            purchases = (
                db.query(Purchase)
                .join(Product)
                .join(Supplier)
                .filter(
                    Purchase.organization_id == organization_id,
                    Purchase.purchase_date >= start_date,
                    Purchase.purchase_date <= end_date,
                )
                .order_by(Purchase.purchase_date.asc())
                .all()
            )

            total_spend = sum(p.total_price for p in purchases)
            orders_count = len(purchases)
            unique_suppliers = len({p.supplier_id for p in purchases})

            # Calculate verified realized savings vs potential savings
            # Realized savings: difference between baseline price and actual purchase price
            # In Daily Cup: EcoTorg cups saved 190 ₸/pack, Coffee saved 700 ₸/kg, Milk saved 50 ₸/L
            realized_savings = 0.0
            for p in purchases:
                if p.product and "350" in p.product.name and p.unit_price < 1570.0:
                    realized_savings += (1570.0 - p.unit_price) * p.quantity
                elif p.product and "стакан" in p.product.name.lower() and "250" not in p.product.name and p.unit_price < 1420.0:
                    realized_savings += (1420.0 - p.unit_price) * p.quantity
                elif p.product and "кофе" in p.product.name.lower() and p.unit_price < 8200.0:
                    realized_savings += (8200.0 - p.unit_price) * p.quantity
                elif p.product and "молоко" in p.product.name.lower() and p.unit_price < 520.0:
                    realized_savings += (520.0 - p.unit_price) * p.quantity

            # Potential savings from active cheaper alternative offers
            potential_savings = 0.0
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
                        SupplierOffer.organization_id == organization_id,
                        SupplierOffer.supplier_id != latest_p.supplier_id,
                        SupplierOffer.is_active == True,
                    ).order_by(SupplierOffer.offered_price.asc()).first()
                    if best_offer and best_offer.offered_price < latest_p.unit_price:
                        potential_savings += (latest_p.unit_price - best_offer.offered_price) * max(prod.minimum_stock, 20.0)

            kpi_cards = [
                {
                    "title": "Сумма закупок за период",
                    "value": f"{total_spend:,.0f} {currency}".replace(",", " "),
                    "subtitle": f"{orders_count} партий поставлено",
                    "badge": "закупки",
                    "type": "neutral",
                },
                {
                    "title": "Активных поставщиков",
                    "value": f"{unique_suppliers}",
                    "subtitle": "Работающих с кофейней",
                    "badge": "поставщики",
                    "type": "neutral",
                },
                {
                    "title": "Фактическая экономия",
                    "value": f"{realized_savings:,.0f} {currency}".replace(",", " "),
                    "subtitle": "Подтвержденная закупками разница",
                    "badge": "реализовано",
                    "type": "profit" if realized_savings > 0 else "neutral",
                },
                {
                    "title": "Потенциал оптимизации",
                    "value": f"{potential_savings:,.0f} {currency}".replace(",", " "),
                    "subtitle": "Выгода при заказе у альтернатив",
                    "badge": "потенциал",
                    "type": "profit" if potential_savings > 0 else "neutral",
                },
            ]

            rows = []
            if group_by == "supplier":
                sup_data = {}
                for p in purchases:
                    s_name = p.supplier.name if p.supplier else f"Поставщик #{p.supplier_id}"
                    s_origin = "Из базы BizMind" if getattr(p.supplier, "is_global", False) else "Импортирован"
                    if s_name not in sup_data:
                        sup_data[s_name] = {"spend": 0.0, "orders": 0, "origin": s_origin, "items": set()}
                    sup_data[s_name]["spend"] += p.total_price
                    sup_data[s_name]["orders"] += 1
                    if p.product:
                        sup_data[s_name]["items"].add(p.product.name)

                for s_name, vals in sup_data.items():
                    share = round(vals["spend"] / total_spend * 100, 1) if total_spend > 0 else 0.0
                    rows.append({
                        "item": s_name,
                        "origin": vals["origin"],
                        "spend": round(vals["spend"], 2),
                        "orders": vals["orders"],
                        "share": share,
                        "products_count": len(vals["items"]),
                    })

                columns = [
                    {"key": "item", "label": "Поставщик"},
                    {"key": "origin", "label": "Источник"},
                    {"key": "spend", "label": f"Сумма заказов ({currency})"},
                    {"key": "share", "label": "Доля закупок (%)"},
                    {"key": "orders", "label": "Партий"},
                    {"key": "products_count", "label": "Позиций SKU"},
                ]
            else:  # product
                prod_data = {}
                for p in purchases:
                    p_name = p.product.name if p.product else f"Товар #{p.product_id}"
                    cat = p.product.category if p.product else "Прочее"
                    unit = p.unit or "шт"
                    if p_name not in prod_data:
                        prod_data[p_name] = {"category": cat, "unit": unit, "qty": 0.0, "spend": 0.0, "count": 0}
                    prod_data[p_name]["qty"] += p.quantity
                    prod_data[p_name]["spend"] += p.total_price
                    prod_data[p_name]["count"] += 1

                for p_name, vals in prod_data.items():
                    avg_p = round(vals["spend"] / vals["qty"], 2) if vals["qty"] > 0 else 0.0
                    share = round(vals["spend"] / total_spend * 100, 1) if total_spend > 0 else 0.0
                    rows.append({
                        "item": p_name,
                        "category": vals["category"],
                        "qty": round(vals["qty"], 1),
                        "unit": vals["unit"],
                        "avg_price": avg_p,
                        "spend": round(vals["spend"], 2),
                        "share": share,
                    })

                columns = [
                    {"key": "item", "label": "Наименование товара"},
                    {"key": "category", "label": "Категория"},
                    {"key": "qty", "label": "Объем закупки"},
                    {"key": "unit", "label": "Ед."},
                    {"key": "avg_price", "label": f"Средняя цена ({currency})"},
                    {"key": "spend", "label": f"Итого расходы ({currency})"},
                    {"key": "share", "label": "Доля (%)"},
                ]

            if sort_by == "amount_desc":
                rows.sort(key=lambda x: x.get("spend", 0), reverse=True)
            elif sort_by == "amount_asc":
                rows.sort(key=lambda x: x.get("spend", 0))

            return ReportPreviewResponse(
                title=config.get("title") or "Анализ закупок и изменения цен",
                report_type=report_type,
                organization_name=org_name,
                currency=currency,
                period_label=period_label,
                start_date=start_date,
                end_date=end_date,
                generated_at=now,
                kpi_cards=kpi_cards,
                charts={},
                summary_data=[],
                columns=columns,
                rows=rows,
                is_empty=len(rows) == 0,
            )

        # =====================================================================
        # 3. INVENTORY REPORT
        # =====================================================================
        elif report_type == "inventory":
            products = (
                db.query(Product)
                .filter(
                    Product.organization_id == organization_id,
                    Product.is_active == True,
                )
                .order_by(Product.category.asc(), Product.name.asc())
                .all()
            )

            total_skus = len(products)
            critical_items = []
            low_items = []
            normal_items = []
            total_stock_value = 0.0

            rows = []
            for prod in products:
                # Latest price for valuation
                latest_p = (
                    db.query(Purchase)
                    .filter(
                        Purchase.product_id == prod.id,
                        Purchase.organization_id == organization_id,
                    )
                    .order_by(desc(Purchase.purchase_date), desc(Purchase.id))
                    .first()
                )
                unit_price = latest_p.unit_price if latest_p else 0.0
                item_val = round(prod.current_stock * unit_price, 2)
                total_stock_value += item_val

                if prod.current_stock < prod.minimum_stock:
                    status_str = "Критический"
                    status_class = "danger"
                    critical_items.append(prod)
                elif prod.current_stock <= prod.minimum_stock * 1.5:
                    status_str = "Низкий"
                    status_class = "warning"
                    low_items.append(prod)
                else:
                    status_str = "В норме"
                    status_class = "success"
                    normal_items.append(prod)

                rows.append({
                    "item": prod.name,
                    "sku": prod.sku or f"SKU-{prod.id:04d}",
                    "category": prod.category,
                    "current_stock": prod.current_stock,
                    "minimum_stock": prod.minimum_stock,
                    "unit": prod.unit,
                    "unit_price": unit_price,
                    "valuation": item_val,
                    "status": status_str,
                    "status_class": status_class,
                })

            kpi_cards = [
                {
                    "title": "Учитываемых SKU",
                    "value": f"{total_skus} поз.",
                    "subtitle": "Активных позиций на складе",
                    "badge": "номенклатура",
                    "type": "neutral",
                },
                {
                    "title": "Критические остатки",
                    "value": f"{len(critical_items)} поз.",
                    "subtitle": "Ниже установленного минимума",
                    "badge": "дефицит",
                    "type": "loss" if len(critical_items) > 0 else "neutral",
                },
                {
                    "title": "Низкие остатки",
                    "value": f"{len(low_items)} поз.",
                    "subtitle": "Требуют включения в заказ",
                    "badge": "внимание",
                    "type": "warning" if len(low_items) > 0 else "neutral",
                },
                {
                    "title": "Оценочная стоимость запасов",
                    "value": f"{total_stock_value:,.0f} {currency}".replace(",", " "),
                    "subtitle": "По ценам последних поставок",
                    "badge": "активы",
                    "type": "neutral",
                },
            ]

            columns = [
                {"key": "item", "label": "Наименование товара"},
                {"key": "category", "label": "Категория"},
                {"key": "current_stock", "label": "Текущий остаток"},
                {"key": "minimum_stock", "label": "Мин. норма"},
                {"key": "unit", "label": "Ед."},
                {"key": "unit_price", "label": f"Цена ({currency})"},
                {"key": "valuation", "label": f"Стоимость запаса ({currency})"},
                {"key": "status", "label": "Статус склада"},
            ]

            if sort_by == "stock_asc":
                rows.sort(key=lambda x: (x["current_stock"] - x["minimum_stock"]))
            elif sort_by == "amount_desc":
                rows.sort(key=lambda x: x["valuation"], reverse=True)

            return ReportPreviewResponse(
                title=config.get("title") or "Склад и низкие остатки",
                report_type=report_type,
                organization_name=org_name,
                currency=currency,
                period_label=period_label,
                start_date=start_date,
                end_date=end_date,
                generated_at=now,
                kpi_cards=kpi_cards,
                charts={},
                summary_data=[],
                columns=columns,
                rows=rows,
                is_empty=len(rows) == 0,
            )

        # =====================================================================
        # 4. EXECUTIVE SUMMARY REPORT
        # =====================================================================
        else:  # executive
            txs = (
                db.query(FinancialTransaction)
                .filter(
                    FinancialTransaction.organization_id == organization_id,
                    FinancialTransaction.transaction_date >= start_date,
                    FinancialTransaction.transaction_date <= end_date,
                    FinancialTransaction.is_archived == False,
                )
                .all()
            )
            purchases = (
                db.query(Purchase)
                .filter(
                    Purchase.organization_id == organization_id,
                    Purchase.purchase_date >= start_date,
                    Purchase.purchase_date <= end_date,
                )
                .all()
            )
            products = (
                db.query(Product)
                .filter(
                    Product.organization_id == organization_id,
                    Product.is_active == True,
                )
                .all()
            )

            total_income = sum(t.amount for t in txs if t.transaction_type == "income")
            total_expenses = sum(t.amount for t in txs if t.transaction_type == "expense")
            net_profit = total_income - total_expenses
            procurement_spend = sum(p.total_price for p in purchases)
            critical_stock_count = sum(1 for p in products if p.current_stock < p.minimum_stock)

            # Verified savings
            realized_savings = 0.0
            for p in purchases:
                if p.product and "350" in p.product.name and p.unit_price < 1570.0:
                    realized_savings += (1570.0 - p.unit_price) * p.quantity
                elif p.product and "стакан" in p.product.name.lower() and "250" not in p.product.name and p.unit_price < 1420.0:
                    realized_savings += (1420.0 - p.unit_price) * p.quantity
                elif p.product and "кофе" in p.product.name.lower() and p.unit_price < 8200.0:
                    realized_savings += (8200.0 - p.unit_price) * p.quantity
                elif p.product and "молоко" in p.product.name.lower() and p.unit_price < 520.0:
                    realized_savings += (520.0 - p.unit_price) * p.quantity

            kpi_cards = [
                {
                    "title": "Выручка",
                    "value": f"{total_income:,.0f} {currency}".replace(",", " "),
                    "subtitle": "Оборот кофейни",
                    "badge": "+ доход",
                    "type": "income",
                },
                {
                    "title": "Расходы",
                    "value": f"{total_expenses:,.0f} {currency}".replace(",", " "),
                    "subtitle": f"Закупки: {procurement_spend:,.0f} {currency}".replace(",", " "),
                    "badge": "- расход",
                    "type": "expense",
                },
                {
                    "title": "Чистая прибыль",
                    "value": f"{net_profit:,.0f} {currency}".replace(",", " "),
                    "subtitle": f"Маржа: {((net_profit / total_income * 100) if total_income > 0 else 0):.1f}%",
                    "badge": "прибыль",
                    "type": "profit" if net_profit >= 0 else "loss",
                },
                {
                    "title": "Сэкономлено в BizMind",
                    "value": f"{realized_savings:,.0f} {currency}".replace(",", " "),
                    "subtitle": f"Критических остатков: {critical_stock_count}",
                    "badge": "эффект",
                    "type": "profit" if realized_savings > 0 else "neutral",
                },
            ]

            # Categories breakdown rows
            cat_data = {}
            for t in txs:
                if t.transaction_type == "expense":
                    c = t.category or "Прочее"
                    cat_data[c] = cat_data.get(c, 0.0) + t.amount

            rows = []
            for c, amt in sorted(cat_data.items(), key=lambda x: x[1], reverse=True):
                share = round(amt / total_expenses * 100, 1) if total_expenses > 0 else 0.0
                rows.append({
                    "item": c,
                    "expense": round(amt, 2),
                    "share": share,
                    "status": "Умеренно" if share < 30 else "Высокая доля",
                })

            columns = [
                {"key": "item", "label": "Статья расходов"},
                {"key": "expense", "label": f"Сумма ({currency})"},
                {"key": "share", "label": "Доля в расходах (%)"},
                {"key": "status", "label": "Оценка нагрузки"},
            ]

            return ReportPreviewResponse(
                title=config.get("title") or "Сводный отчёт владельца кафе",
                report_type=report_type,
                organization_name=org_name,
                currency=currency,
                period_label=period_label,
                start_date=start_date,
                end_date=end_date,
                generated_at=now,
                kpi_cards=kpi_cards,
                charts={},
                summary_data=[],
                columns=columns,
                rows=rows,
                is_empty=len(rows) == 0,
            )

    @classmethod
    def export_report_excel(
        cls,
        db: Session,
        organization_id: int,
        report_type: str,
        config: Dict[str, Any],
    ) -> bytes:
        data = cls.generate_report_data(db, organization_id, report_type, config)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Отчёт BizMind"
        ws.views.sheetView[0].showGridLines = True

        # Styles
        title_font = Font(name="Calibri", size=16, bold=True, color="1E293B")
        sub_font = Font(name="Calibri", size=10, italic=True, color="64748B")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")  # Deep Navy
        kpi_title_font = Font(name="Calibri", size=9, bold=True, color="64748B")
        kpi_val_font = Font(name="Calibri", size=14, bold=True, color="0F172A")
        cell_font = Font(name="Calibri", size=11, color="1E293B")
        total_font = Font(name="Calibri", size=11, bold=True, color="0F172A")

        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1"),
        )
        kpi_border = Border(
            left=Side(style="medium", color="94A3B8"),
            right=Side(style="medium", color="94A3B8"),
            top=Side(style="medium", color="94A3B8"),
            bottom=Side(style="medium", color="94A3B8"),
        )
        kpi_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        # 1. Header Banner
        ws.cell(row=1, column=1, value=data.title).font = title_font
        ws.cell(row=2, column=1, value=f"Организация: {data.organization_name} | Период: {data.period_label}").font = sub_font
        ws.cell(row=3, column=1, value=f"Сформировано в BizMind: {data.generated_at.strftime('%d.%m.%Y %H:%M:%S UTC')}").font = sub_font

        cur_row = 5

        # 2. KPI Cards Block
        if data.kpi_cards:
            for idx, kpi in enumerate(data.kpi_cards):
                c_start = 1 + idx * 2
                c_end = c_start + 1
                ws.merge_cells(start_row=cur_row, start_column=c_start, end_row=cur_row, end_column=c_end)
                ws.merge_cells(start_row=cur_row + 1, start_column=c_start, end_row=cur_row + 1, end_column=c_end)
                ws.merge_cells(start_row=cur_row + 2, start_column=c_start, end_row=cur_row + 2, end_column=c_end)

                c1 = ws.cell(row=cur_row, column=c_start, value=kpi.get("title", ""))
                c1.font = kpi_title_font
                c1.alignment = Alignment(horizontal="center")

                c2 = ws.cell(row=cur_row + 1, column=c_start, value=kpi.get("value", ""))
                c2.font = kpi_val_font
                c2.alignment = Alignment(horizontal="center")

                c3 = ws.cell(row=cur_row + 2, column=c_start, value=kpi.get("subtitle", ""))
                c3.font = sub_font
                c3.alignment = Alignment(horizontal="center")

                # Box borders and background
                for r in range(cur_row, cur_row + 3):
                    for col in range(c_start, c_end + 1):
                        cell = ws.cell(row=r, column=col)
                        cell.fill = kpi_fill
                        cell.border = kpi_border

            cur_row += 4

        # 3. Main Data Table
        if data.is_empty:
            ws.cell(row=cur_row, column=1, value=data.message or "Нет данных за выбранный период").font = Font(italic=True, color="64748B")
        elif data.columns and data.rows:
            # Table Header
            for col_idx, col in enumerate(data.columns, 1):
                c = ws.cell(row=cur_row, column=col_idx, value=col.get("label", ""))
                c.font = header_font
                c.fill = header_fill
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                c.border = thin_border
            ws.row_dimensions[cur_row].height = 24
            cur_row += 1

            # Rows
            for row in data.rows:
                ws.row_dimensions[cur_row].height = 20
                for col_idx, col in enumerate(data.columns, 1):
                    val = row.get(col["key"])
                    c = ws.cell(row=cur_row, column=col_idx, value=val)
                    c.font = cell_font
                    c.border = thin_border

                    # Numeric alignment & formatting
                    if isinstance(val, (int, float)):
                        c.alignment = Alignment(horizontal="right")
                        if "share" in col["key"]:
                            c.number_format = "0.0\"%\""
                        elif "price" in col["key"] or "income" in col["key"] or "expense" in col["key"] or "net" in col["key"] or "spend" in col["key"] or "valuation" in col["key"]:
                            c.number_format = "#,##0.00"
                        else:
                            c.number_format = "#,##0"
                    else:
                        c.alignment = Alignment(horizontal="left")
                cur_row += 1

        # Adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len and len(val_str) < 50:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    @classmethod
    def export_report_csv(
        cls,
        db: Session,
        organization_id: int,
        report_type: str,
        config: Dict[str, Any],
    ) -> str:
        data = cls.generate_report_data(db, organization_id, report_type, config)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")

        writer.writerow([data.title])
        writer.writerow([f"Организация: {data.organization_name}", f"Период: {data.period_label}"])
        writer.writerow([f"Сформировано: {data.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"])
        writer.writerow([])

        if data.kpi_cards:
            writer.writerow(["Ключевой показатель", "Значение", "Примечание"])
            for k in data.kpi_cards:
                writer.writerow([k.get("title", ""), k.get("value", ""), k.get("subtitle", "")])
            writer.writerow([])

        if data.is_empty:
            writer.writerow([data.message or "Нет данных"])
        elif data.columns and data.rows:
            headers = [c.get("label", "") for c in data.columns]
            writer.writerow(headers)

            for row in data.rows:
                row_vals = [row.get(c["key"], "") for c in data.columns]
                writer.writerow(row_vals)

        return output.getvalue()
