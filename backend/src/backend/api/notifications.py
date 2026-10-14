from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.schemas.schemas import NotificationResponse
from backend.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return NotificationService.get_notifications(
        db=db, organization_id=organization_id, unread_only=unread_only, limit=limit
    )

@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    success = NotificationService.mark_as_read(
        db=db, notification_id=notification_id, organization_id=organization_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    return {"status": "ok", "id": notification_id}

@router.post("/read-all")
def mark_all_read(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    count = NotificationService.mark_all_as_read(db=db, organization_id=organization_id)
    return {"status": "ok", "marked_count": count}
