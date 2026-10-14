from datetime import date, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.models import Product, Purchase
from backend.schemas.schemas import ForecastItem, ForecastSummary


class ForecastService:
    @staticmethod
    def get_forecast(
        db: Session,
        organization_id: int = 1,
    ) -> ForecastSummary:
        products = db.query(Product).filter(
            Product.organization_id == organization_id
        ).order_by(Product.category.asc(), Product.name.asc()).all()

        items: List[ForecastItem] = []
        critical_count = 0
        low_count = 0

        today = date(2026, 10, 14)
        cutoff_date = today - timedelta(days=90)

        for prod in products:
            # Get purchases in the last 90 days
            purchases = db.query(Purchase).filter(
                Purchase.product_id == prod.id,
                Purchase.organization_id == organization_id,
                Purchase.purchase_date >= cutoff_date,
            ).order_by(Purchase.purchase_date.asc()).all()

            total_qty = sum(p.quantity for p in purchases)
            
            if purchases and len(purchases) >= 2:
                earliest = purchases[0].purchase_date
                latest = purchases[-1].purchase_date
                days_span = max(14, (latest - earliest).days)
                avg_daily = round(total_qty / days_span, 2)
            elif purchases and len(purchases) == 1:
                avg_daily = round(total_qty / 30.0, 2)
            else:
                avg_daily = 0.5  # fallback baseline

            if avg_daily > 0:
                days_left = round(prod.current_stock / avg_daily, 1)
                forecast_7d = round(avg_daily * 7, 1)
                forecast_14d = round(avg_daily * 14, 1)
                forecast_30d = round(avg_daily * 30, 1)
                recommended_order = max(
                    0.0, round((forecast_14d + prod.minimum_stock) - prod.current_stock, 1)
                )
            else:
                days_left = 999.0
                forecast_7d = 0.0
                forecast_14d = 0.0
                forecast_30d = 0.0
                recommended_order = max(0.0, prod.minimum_stock - prod.current_stock)

            if prod.current_stock < prod.minimum_stock or (days_left is not None and days_left <= 3):
                status = "critical"
                critical_count += 1
                note = f"Критически низкий остаток ({prod.current_stock} {prod.unit}). Запаса хватит менее чем на 3 дня!"
            elif days_left is not None and days_left <= 7:
                status = "low"
                low_count += 1
                note = f"Запас на исходе ({prod.current_stock} {prod.unit}). Рекомендуется оформить заказ в течение 2-3 дней."
            else:
                status = "normal"
                note = f"Запас в пределах нормы ({prod.current_stock} {prod.unit}). Ориентировочно на {int(days_left)} дн."

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
                    note=note,
                )
            )

        # Sort: critical first, then low, then normal
        status_priority = {"critical": 0, "low": 1, "normal": 2}
        items.sort(key=lambda x: (status_priority.get(x.status, 3), x.days_left or 999))

        return ForecastSummary(
            total_products_tracked=len(products),
            critical_items_count=critical_count,
            low_stock_items_count=low_count,
            items=items,
        )
