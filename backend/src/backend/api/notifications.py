from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.schemas import NotificationResponse
from backend.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
):
    return NotificationService.get_notifications(
        db=db, organization_id=1, unread_only=unread_only, limit=limit
    )

@router.post("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    success = NotificationService.mark_as_read(
        db=db, notification_id=notification_id, organization_id=1
    )
    if not success:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    return {"status": "ok", "id": notification_id}

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    count = NotificationService.mark_all_as_read(db=db, organization_id=1)
    return {"status": "ok", "marked_count": count}
