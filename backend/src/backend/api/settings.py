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
        if len(data.name.strip()) < 2:
            raise HTTPException(status_code=422, detail="Название организации должно содержать минимум 2 символа")
        org.name = data.name.strip()

    if data.business_type is not None:
        org.business_type = data.business_type.strip()

    if data.currency is not None:
        org.currency = data.currency.strip()

    threshold = data.alert_threshold_percent if data.alert_threshold_percent is not None else data.price_alert_threshold_percent
    if threshold is not None:
        if threshold < 0.1 or threshold > 100.0:
            raise HTTPException(status_code=422, detail="Порог алерта о росте цен должен быть в диапазоне от 0.1% до 100%")
        org.alert_threshold_percent = round(float(threshold), 2)

    if data.address is not None:
        org.address = data.address.strip()

    phone_val = data.phone if data.phone is not None else data.contact_phone
    if phone_val is not None:
        org.phone = phone_val.strip()

    email_val = data.email if data.email is not None else data.contact_email
    if email_val is not None:
        clean_email = email_val.strip().lower()
        if clean_email and ("@" not in clean_email or "." not in clean_email):
            raise HTTPException(status_code=422, detail="Некорректный формат контактного email")
        org.email = clean_email

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


@router.get("/activity", response_model=List[ActivityLogResponse])
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
            user_name=l.user.name if l.user else (l.user_name or "Система"),
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
    if not data.name or len(data.name.strip()) < 2:
        raise HTTPException(status_code=422, detail="Имя сотрудника должно содержать минимум 2 символа")

    email_clean = data.email.strip().lower()
    if "@" not in email_clean or "." not in email_clean:
        raise HTTPException(status_code=422, detail="Некорректный формат email сотрудника")

    if not data.password or len(data.password) < 6:
        raise HTTPException(status_code=422, detail="Пароль должен содержать минимум 6 символов")

    role_val = data.role.lower().strip()
    if role_val not in ["owner", "manager", "employee"]:
        raise HTTPException(status_code=422, detail="Недопустимая роль. Доступно: owner, manager, employee")

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

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
