from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import User, Organization
from backend.schemas.schemas import (
    UserResponse,
    UserLoginRequest,
    OrganizationResponse,
    OrganizationInfo,
    OrganizationSwitchRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Авторизация пользователя по email и паролю."""
    from backend.security import verify_password

    email_clean = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if user.password_hash:
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if user.is_active is False:
        raise HTTPException(status_code=403, detail="Учетная запись деактивирована")

    return user



def _get_org_info(org: Organization, user: Optional[User]) -> OrganizationInfo:
    if org.id == 1:
        scenario_type = "initial_adoption"
        scenario_title = "Первоначальное внедрение"
        scenario_description = (
            "Действующая кофейня на этапе внедрения BizMind. Исторические данные еще не загружены. "
            "Демонстрация чистого старта и пошагового импорта финансовых операций, закупок и прайс-листов."
        )
        demo_badge = "Первоначальное внедрение (чистый старт)"
    else:
        scenario_type = "regular_usage"
        scenario_title = "Регулярное использование"
        scenario_description = (
            "Сетевая кофейня To-Go, системно работающая в BizMind 6 месяцев. "
            "Демонстрация подтвержденной экономии (153 200 ₸), смены поставщиков упаковки и контроля запасов."
        )
        demo_badge = "Регулярное использование (6 месяцев)"

    return OrganizationInfo(
        id=org.id,
        name=org.name,
        business_type=org.business_type or "Кофейня",
        scenario_type=scenario_type,
        scenario_title=scenario_title,
        scenario_description=scenario_description,
        demo_badge=demo_badge,
        user_name=user.name if user else "Демо-пользователь",
        user_email=user.email if user else "demo@bizmind.kz",
        user_role=user.role if user else "Управляющий",
        created_at=org.created_at,
    )


@router.get("/organizations", response_model=List[OrganizationInfo])
def list_organizations(db: Session = Depends(get_db)):
    """
    Returns available demo spaces with scenario metadata.
    """
    orgs = db.query(Organization).order_by(Organization.id.asc()).all()
    results: List[OrganizationInfo] = []
    for org in orgs:
        user = db.query(User).filter(User.organization_id == org.id).first()
        results.append(_get_org_info(org, user))
    return results


@router.post("/demo-login", response_model=UserResponse)
def demo_login(
    org_id: Optional[int] = Query(None),
    x_org_id: Optional[str] = Header(None, alias="X-Organization-Id"),
    db: Session = Depends(get_db)
):
    target_org_id = 1
    if org_id is not None and org_id > 0:
        target_org_id = org_id
    elif x_org_id and x_org_id.strip().isdigit():
        target_org_id = int(x_org_id.strip())

    user = db.query(User).filter(User.organization_id == target_org_id).first()
    if not user:
        user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.post("/switch-org", response_model=UserResponse)
def switch_organization(
    payload: OrganizationSwitchRequest,
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Организация не найдена")

    user = db.query(User).filter(User.organization_id == payload.organization_id).first()
    if not user:
        # Create a default user if missing
        user = User(
            organization_id=org.id,
            name=f"Управляющий {org.name}",
            email=f"demo_org_{org.id}@bizmind.kz",
            role="Управляющий / Владелец",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user(
    x_org_id: Optional[str] = Header(None, alias="X-Organization-Id"),
    db: Session = Depends(get_db)
):
    target_org_id = 1
    if x_org_id and x_org_id.strip().isdigit():
        target_org_id = int(x_org_id.strip())

    user = db.query(User).filter(User.organization_id == target_org_id).first()
    if not user:
        user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="Демо-пользователь не найден")
    return user
