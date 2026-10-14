from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.models import Notification
from backend.schemas.schemas import NotificationResponse


class NotificationService:
    @staticmethod
    def get_notifications(
        db: Session,
        organization_id: int = 1,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[NotificationResponse]:
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
