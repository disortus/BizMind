from typing import Optional, List, Callable, Any
from fastapi import Header, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import Organization, User, ActivityLog


def get_current_organization_id(
    x_org_id: Optional[str] = Header(None, alias="X-Organization-Id"),
    org_id: Optional[int] = Query(None, alias="org_id"),
    db: Session = Depends(get_db)
) -> int:
    """
    Extracts active organization ID from request header or query parameter.
    Validates that the organization exists, defaulting safely to Org 1 if invalid or absent.
    """
    candidate_id: Optional[int] = None
    if x_org_id and x_org_id.strip().isdigit():
        candidate_id = int(x_org_id.strip())
    elif org_id is not None and org_id > 0:
        candidate_id = org_id

    if candidate_id:
        exists = db.query(Organization.id).filter(Organization.id == candidate_id).scalar()
        if exists:
            return candidate_id

    # Fallback to organization 1 or first available
    first_org = db.query(Organization.id).order_by(Organization.id.asc()).first()
    if first_org:
        return first_org[0]
    return 1


def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
) -> User:
    """
    Retrieves the currently authenticated user for the active organization.
    If X-User-Id is provided, validates that the user belongs to the active organization.
    Otherwise returns the primary user for that organization.
    """
    user: Optional[User] = None
    if x_user_id and x_user_id.strip().isdigit():
        uid = int(x_user_id.strip())
        user = db.query(User).filter(User.id == uid, User.organization_id == organization_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не принадлежит выбранной организации"
            )

    if not user:
        # Default user of the organization
        user = db.query(User).filter(User.organization_id == organization_id).order_by(User.id.asc()).first()

    if not user:
        # Fallback create a default user if none exists in organization
        user = User(
            organization_id=organization_id,
            name="Администратор",
            email=f"admin_{organization_id}@bizmind.local",
            role="owner",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory checking if current user has one of the allowed roles.
    Supports both standard lowercase roles ('owner', 'manager', 'employee')
    and Russian display strings ('Владелец', 'Управляющий', 'Бариста').
    """
    def role_checker(user: User = Depends(get_current_user)) -> User:
        user_role = (user.role or "").lower()
        allowed = [r.lower() for r in allowed_roles]

        # Normalize hierarchy: Owner > Manager > Employee
        is_owner = any(w in user_role for w in ["owner", "владелец", "директор"])
        is_manager = any(w in user_role for w in ["manager", "управляющий", "менеджер"]) or is_owner
        is_employee = any(w in user_role for w in ["employee", "сотрудник", "бариста"]) or is_manager

        if "owner" in allowed and is_owner:
            return user
        if "manager" in allowed and is_manager:
            return user
        if "employee" in allowed and is_employee:
            return user

        if any(r in user_role for r in allowed):
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Недостаточно прав. Требуется роль: {', '.join(allowed_roles)}"
        )
    return role_checker


def log_activity(
    db: Session,
    organization_id: int,
    action: str,
    entity: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[Any] = None,
    details: Optional[str] = None,
    user_id: Optional[int] = None,
    user: Optional[User] = None,
):
    """
    Records an entry in the organization's ActivityLog.
    """
    try:
        e_type = entity_type or entity or "General"
        uid = user.id if user else user_id
        uname = user.name if user else ("Система" if not uid else None)
        if uid and not uname:
            u_obj = db.query(User).filter(User.id == uid).first()
            if u_obj:
                uname = u_obj.name

        entry = ActivityLog(
            organization_id=organization_id,
            user_id=uid,
            user_name=uname or "Система",
            action=action,
            entity_type=e_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            details=details,
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
