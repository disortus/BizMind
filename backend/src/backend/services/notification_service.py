from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from backend.models.models import (
    Notification,
    Product,
    Supplier,
    SupplierOffer,
    PurchaseOrder,
    Organization,
)
from backend.schemas.schemas import NotificationResponse


class NotificationService:
    @staticmethod
    def get_notifications(
        db: Session,
        organization_id: int = 1,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[NotificationResponse]:
        # Proactively check and generate condition-based notifications
        NotificationService.generate_system_notifications(db, organization_id)

        query = db.query(Notification).filter(
            Notification.organization_id == organization_id
        )
        if unread_only:
            query = query.filter(Notification.is_read == False)

        notifications = query.order_by(
            Notification.is_read.asc(), desc(Notification.created_at)
        ).limit(limit).all()

        return [
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
            for n in notifications
        ]

    @staticmethod
    def generate_system_notifications(db: Session, organization_id: int = 1) -> int:
        """
        Сканирует бизнес-правила и создает уведомления, если аналогичное непрочитанное еще не создано:
        - Остаток ниже установленного минимума
        - Устаревший прайс-лист (> 30 дней)
        - Заказ закупки в статусе Draft требует внимания
        """
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        created_count = 0

        # 1. Low stock alerts
        products = db.query(Product).filter(
            Product.organization_id == organization_id,
            Product.is_active == True,
            Product.current_stock < Product.minimum_stock,
        ).all()

        for p in products:
            existing = db.query(Notification).filter(
                Notification.organization_id == organization_id,
                Notification.notification_type == "low_stock",
                Notification.related_product_id == p.id,
                Notification.is_read == False,
            ).first()
            if not existing:
                severity = "critical" if p.current_stock <= (p.minimum_stock * 0.5) else "warning"
                notif = Notification(
                    organization_id=organization_id,
                    title=f"Дефицит: {p.name}",
                    description=f"Текущий остаток {p.current_stock} {p.unit} ниже минимума {p.minimum_stock} {p.unit}. Рекомендуется сформировать заказ поставщику.",
                    severity=severity,
                    notification_type="low_stock",
                    related_product_id=p.id,
                    is_read=False,
                    created_at=datetime.utcnow(),
                )
                db.add(notif)
                created_count += 1

        # 2. Stale price lists (> 30 days)
        stale_cutoff = datetime.utcnow() - timedelta(days=30)
        stale_offers = db.query(SupplierOffer).filter(
            SupplierOffer.organization_id == organization_id,
            SupplierOffer.is_active == True,
            SupplierOffer.updated_at < stale_cutoff,
        ).limit(5).all()

        for o in stale_offers:
            existing = db.query(Notification).filter(
                Notification.organization_id == organization_id,
                Notification.notification_type == "stale_price",
                Notification.related_product_id == o.product_id,
                Notification.is_read == False,
            ).first()
            if not existing and o.product and o.supplier:
                notif = Notification(
                    organization_id=organization_id,
                    title=f"Устаревший прайс: {o.supplier.name}",
                    description=f"Прайс на '{o.product.name}' не обновлялся более 30 дней. Рекомендуется запросить свежий прайс-лист.",
                    severity="info",
                    notification_type="stale_price",
                    related_product_id=o.product_id,
                    is_read=False,
                    created_at=datetime.utcnow(),
                )
                db.add(notif)
                created_count += 1

        # 3. Draft purchase orders requiring confirmation
        draft_orders = db.query(PurchaseOrder).filter(
            PurchaseOrder.organization_id == organization_id,
            PurchaseOrder.status == "draft",
        ).all()

        for order in draft_orders:
            existing = db.query(Notification).filter(
                Notification.organization_id == organization_id,
                Notification.notification_type == "draft_order",
                Notification.description.like(f"%{order.order_number}%"),
                Notification.is_read == False,
            ).first()
            if not existing:
                notif = Notification(
                    organization_id=organization_id,
                    title=f"Черновик заказа #{order.order_number}",
                    description=f"Заказ #{order.order_number} ({order.supplier_name}, {order.total_amount} ₸) находится в статусе черновика и ожидает согласования.",
                    severity="warning",
                    notification_type="draft_order",
                    is_read=False,
                    created_at=datetime.utcnow(),
                )
                db.add(notif)
                created_count += 1

        if created_count > 0:
            db.commit()

        return created_count

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        organization_id: int = 1,
    ) -> bool:
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.organization_id == organization_id
        ).first()
        if notif:
            notif.is_read = True
            db.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(
        db: Session,
        organization_id: int = 1,
    ) -> int:
        count = db.query(Notification).filter(
            Notification.organization_id == organization_id,
            Notification.is_read == False,
        ).update({"is_read": True})
        db.commit()
        return count
