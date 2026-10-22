from datetime import date, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.models import Product, Purchase, InventoryMovement
from backend.schemas.schemas import ForecastItem, ForecastSummary


class ForecastService:
    @staticmethod
    def get_forecast(
        db: Session,
        organization_id: int = 1,
    ) -> ForecastSummary:
        products = db.query(Product).filter(
            Product.organization_id == organization_id,
            Product.is_active == True,
        ).order_by(Product.category.asc(), Product.name.asc()).all()

        items: List[ForecastItem] = []
        critical_count = 0
        low_count = 0

        # Dynamically determine the reference date: latest purchase or transaction date, or today
        max_purchase_date = db.query(func.max(Purchase.purchase_date)).filter(
            Purchase.organization_id == organization_id
        ).scalar()

        today = max_purchase_date or date.today()
        cutoff_date = today - timedelta(days=90)

        for prod in products:
            # 1. Historical purchases in 90d window
            purchases = db.query(Purchase).filter(
                Purchase.product_id == prod.id,
                Purchase.organization_id == organization_id,
                Purchase.purchase_date >= cutoff_date,
            ).order_by(Purchase.purchase_date.asc()).all()

            total_purchased_qty = sum(p.quantity for p in purchases)

            # 2. Inventory movements (write-offs or negative adjustments)
            write_offs = db.query(InventoryMovement).filter(
                InventoryMovement.product_id == prod.id,
                InventoryMovement.organization_id == organization_id,
                InventoryMovement.movement_type.in_(["write_off", "adjustment"]),
                InventoryMovement.quantity < 0,
            ).all()
            total_consumed_moves = abs(sum(m.quantity for m in write_offs))

            # Determine consumption rate
            if len(purchases) >= 2:
                earliest = purchases[0].purchase_date
                latest = purchases[-1].purchase_date
                days_span = max(14, (latest - earliest).days)
                avg_daily = round((total_purchased_qty + total_consumed_moves) / days_span, 2)
                method_str = f"Среднесуточный run-rate ({days_span} дн., {len(purchases)} поставок)"
                has_sufficient_data = True
            elif len(purchases) == 1:
                avg_daily = round((total_purchased_qty + total_consumed_moves) / 30.0, 2)
                method_str = "Оценка по единичной закупке (окно 30 дн.)"
                has_sufficient_data = True
            elif total_consumed_moves > 0:
                avg_daily = round(total_consumed_moves / 30.0, 2)
                method_str = "Оценка по складским списаниям (окно 30 дн.)"
                has_sufficient_data = True
            else:
                avg_daily = 0.0
                method_str = "Недостаточно данных для прогноза"
                has_sufficient_data = False

            if has_sufficient_data and avg_daily > 0:
                days_left = round(prod.current_stock / avg_daily, 1)
                forecast_7d = round(avg_daily * 7, 1)
                forecast_14d = round(avg_daily * 14, 1)
                forecast_30d = round(avg_daily * 30, 1)
                recommended_order = max(
                    0.0, round((forecast_14d + prod.minimum_stock) - prod.current_stock, 1)
                )

                if prod.current_stock < prod.minimum_stock or (days_left is not None and days_left <= 3):
                    status = "critical"
                    critical_count += 1
                    note = f"Критический остаток ({prod.current_stock} {prod.unit}). Запаса хватит ориентировочно на {days_left} дн.!"
                elif days_left is not None and days_left <= 7:
                    status = "low"
                    low_count += 1
                    note = f"Запас на исходе ({prod.current_stock} {prod.unit}). Хватит на ~{days_left} дн. Рекомендуется заказ."
                else:
                    status = "normal"
                    note = f"Запас в норме ({prod.current_stock} {prod.unit}). Хватит ориентировочно на {int(days_left)} дн."
            else:
                days_left = None
                forecast_7d = 0.0
                forecast_14d = 0.0
                forecast_30d = 0.0
                status = "insufficient_data"
                recommended_order = max(0.0, round(prod.minimum_stock - prod.current_stock, 1))

                if prod.current_stock < prod.minimum_stock:
                    status = "critical"
                    critical_count += 1
                    note = f"Остаток ({prod.current_stock} {prod.unit}) ниже минимума ({prod.minimum_stock} {prod.unit}). Данных о расходе пока нет."
                else:
                    note = f"Недостаточно исторических данных о закупках/расходе. Текущий остаток: {prod.current_stock} {prod.unit}."

            items.append(
                ForecastItem(
                    product_id=prod.id,
                    product_name=prod.name,
                    category=prod.category,
                    unit=prod.unit,
                    current_stock=prod.current_stock,
                    minimum_stock=prod.minimum_stock,
                    avg_daily_consumption=avg_daily,
                    days_left=days_left,
                    forecast_7d=forecast_7d,
                    forecast_14d=forecast_14d,
                    forecast_30d=forecast_30d,
                    recommended_order_quantity=recommended_order,
                    status=status,
                    calculation_method=method_str,
                    note=note,
                )
            )

        # Sort: critical first, then low, then normal, then insufficient_data
        status_priority = {"critical": 0, "low": 1, "normal": 2, "insufficient_data": 3}
        items.sort(key=lambda x: (status_priority.get(x.status, 4), x.days_left if x.days_left is not None else 9999))

        return ForecastSummary(
            total_products_tracked=len(products),
            critical_items_count=critical_count,
            low_stock_items_count=low_count,
            items=items,
        )
