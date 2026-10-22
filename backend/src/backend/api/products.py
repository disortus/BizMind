from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id, get_current_user, require_roles, log_activity
from backend.models.models import User
from backend.schemas.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from backend.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_archived: bool = Query(False),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return ProductService.get_products(
        db=db,
        organization_id=organization_id,
        category=category,
        search=search,
        is_active=is_active,
        include_archived=include_archived,
    )


@router.get("/categories", response_model=List[str])
def get_product_categories(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return ProductService.get_categories(db=db, organization_id=organization_id)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    prod = ProductService.get_product(db=db, product_id=product_id, organization_id=organization_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return prod


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    prod = ProductService.create_product(db=db, data=data, organization_id=organization_id)
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="create",
        entity_type="product",
        entity_id=str(prod.id),
        details=f"Создан товар: {prod.name} ({prod.category}), ост: {prod.current_stock} {prod.unit}",
    )
    return prod


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    prod = ProductService.update_product(
        db=db, product_id=product_id, data=data, organization_id=organization_id
    )
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="update",
        entity_type="product",
        entity_id=str(prod.id),
        details=f"Обновлен товар #{prod.id}: {prod.name}",
    )
    return prod


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    hard_delete: bool = Query(False),
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner"])),
    db: Session = Depends(get_db),
):
    success = ProductService.delete_product(
        db=db, product_id=product_id, organization_id=organization_id, hard_delete=hard_delete
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="delete",
        entity_type="product",
        entity_id=str(product_id),
        details=f"Товар #{product_id} переведен в архив / удален (hard_delete={hard_delete})",
    )
    return {"status": "success", "message": f"Товар #{product_id} успешно архивирован / удален"}
