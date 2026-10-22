from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models.models import Organization, User, ActivityLog
from backend.schemas.schemas import (
    OrganizationResponse,
    OrganizationSettingsUpdate,
    ActivityLogResponse,
    UserResponse,
    UserCreateRequest,
)
from backend.api.deps import get_current_user, require_roles, log_activity
from backend.security import hash_password

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/organization", response_model=OrganizationResponse)
def get_organization_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получение настроек текущей организации."""
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return org


@router.put("/organization", response_model=OrganizationResponse)
def update_organization_settings(
    data: OrganizationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager"])),
):
    """Обновление параметров организации (Owner/Manager)."""
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Организация не найдена")

    if data.name is not None and data.name.strip():
        org.name = data.name.strip()
    if data.business_type is not None:
        org.business_type = data.business_type.strip()
    if data.currency is not None:
        org.currency = data.currency.strip()
    if data.alert_threshold_percent is not None:
        org.alert_threshold_percent = max(0.1, min(100.0, data.alert_threshold_percent))
    if data.address is not None:
        org.address = data.address.strip()
    if data.phone is not None:
        org.phone = data.phone.strip()
    if data.email is not None:
        org.email = data.email.strip()

    db.commit()
    db.refresh(org)

    log_activity(
        db=db,
        organization_id=org.id,
        user_id=current_user.id,
        action="UPDATE_SETTINGS",
        entity="Organization",
        entity_id=org.id,
        details=f"Обновлены настройки организации: {org.name}",
    )
    return org


@router.get("/activity-logs", response_model=List[ActivityLogResponse])
def get_activity_logs(
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Журнал значимых действий и аудита организации."""
    query = db.query(ActivityLog).filter(
        ActivityLog.organization_id == current_user.organization_id
    )
    if action and action != "all":
        query = query.filter(ActivityLog.action == action)

    logs = query.order_by(desc(ActivityLog.created_at)).limit(limit).all()
    return [
        ActivityLogResponse(
            id=l.id,
            organization_id=l.organization_id,
            user_name=l.user.name if l.user else "Система",
            action=l.action,
            entity_type=l.entity_type,
            entity_id=str(l.entity_id) if l.entity_id else None,
            details=l.details,
            created_at=l.created_at,
        )
        for l in logs
    ]


@router.get("/users", response_model=List[UserResponse])
def get_organization_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Список пользователей текущей организации."""
    users = db.query(User).filter(
        User.organization_id == current_user.organization_id,
        User.is_active == True,
    ).order_by(User.role.asc(), User.name.asc()).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_organization_user(
    data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner"])),
):
    """Добавление нового сотрудника в организацию (только Owner)."""
    email_clean = data.email.strip().lower()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    role_val = data.role.lower()
    if role_val not in ["owner", "manager", "employee"]:
        raise HTTPException(status_code=400, detail="Недопустимая роль. Доступно: owner, manager, employee")

    new_user = User(
        organization_id=current_user.organization_id,
        name=data.name.strip(),
        email=email_clean,
        password_hash=hash_password(data.password),
        role=role_val,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_activity(
        db=db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="CREATE_USER",
        entity="User",
        entity_id=new_user.id,
        details=f"Создан пользователь {new_user.name} ({new_user.email}) с ролью {new_user.role}",
    )
    return new_user
