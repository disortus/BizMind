from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from backend.database import get_db
from backend.api.deps import get_current_organization_id, get_current_user, require_roles, log_activity
from backend.models.models import Supplier, SupplierOffer, OfferPriceHistory, Product, User
from backend.schemas.schemas import (
    SupplierResponse,
    SupplierCreate,
    SupplierUpdate,
    SupplierOfferCreate,
    SupplierOfferResponse,
    PriceHistoryItemResponse,
    PriceComparisonResponse,
)
from backend.services.comparison_service import ComparisonService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=List[SupplierResponse])
def get_suppliers(
    is_active: Optional[bool] = None,
    source_type: Optional[str] = Query(None, description="Фильтр по источнику (global, imported, manual)"),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    query = db.query(Supplier).filter(
        or_(
            Supplier.organization_id == organization_id,
            Supplier.is_global == True,
            Supplier.source_type == "global",
        )
    )
    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)
    if source_type:
        query = query.filter(Supplier.source_type == source_type)
    return query.order_by(Supplier.is_global.desc(), Supplier.name.asc()).all()


@router.get("/comparison", response_model=PriceComparisonResponse)
def compare_prices(
    product_id: int = Query(..., description="ID товара для сравнения"),
    quantity: float = Query(20.0, description="Планируемый объем закупки"),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    comparison = ComparisonService.compare_product_offers(
        db=db, product_id=product_id, quantity=quantity, organization_id=organization_id
    )
    if not comparison:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return comparison


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    sup = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        or_(
            Supplier.organization_id == organization_id,
            Supplier.is_global == True,
            Supplier.source_type == "global",
        )
    ).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    return sup


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    data: SupplierCreate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    sup = Supplier(
        organization_id=organization_id,
        name=data.name.strip(),
        contact_name=data.contact_name.strip() if data.contact_name else None,
        phone=data.phone.strip() if data.phone else None,
        email=data.email.strip() if data.email else None,
        address=data.address.strip() if data.address else None,
        notes=data.notes.strip() if data.notes else None,
        delivery_cost=max(0.0, data.delivery_cost),
        minimum_order_amount=max(0.0, data.minimum_order_amount),
        source_type=data.source_type or "manual",
        is_demo=False,
        is_active=True,
    )
    db.add(sup)
    db.commit()
    db.refresh(sup)

    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="create",
        entity_type="supplier",
        entity_id=str(sup.id),
        details=f"Добавлен поставщик: {sup.name} (доставка: {sup.delivery_cost} ₸)",
    )
    return sup


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    sup = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    if sup.is_global or sup.source_type == "global":
        raise HTTPException(
            status_code=403,
            detail="Поставщики из встроенной базы BizMind защищены от изменения и удаления",
        )

    if sup.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if data.name is not None:
        sup.name = data.name.strip()
    if data.contact_name is not None:
        sup.contact_name = data.contact_name.strip()
    if data.phone is not None:
        sup.phone = data.phone.strip()
    if data.email is not None:
        sup.email = data.email.strip()
    if data.address is not None:
        sup.address = data.address.strip()
    if data.notes is not None:
        sup.notes = data.notes.strip()
    if data.delivery_cost is not None:
        sup.delivery_cost = max(0.0, data.delivery_cost)
    if data.minimum_order_amount is not None:
        sup.minimum_order_amount = max(0.0, data.minimum_order_amount)
    if data.is_active is not None:
        sup.is_active = data.is_active

    db.commit()
    db.refresh(sup)

    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="update",
        entity_type="supplier",
        entity_id=str(sup.id),
        details=f"Обновлен поставщик #{sup.id}: {sup.name}",
    )
    return sup


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    hard_delete: bool = Query(False),
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner"])),
    db: Session = Depends(get_db),
):
    sup = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    if sup.is_global or sup.source_type == "global":
        raise HTTPException(
            status_code=403,
            detail="Поставщики из встроенной базы BizMind защищены от изменения и удаления",
        )

    if sup.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if hard_delete:
        db.delete(sup)
    else:
        sup.is_active = False

    db.commit()
    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="delete",
        entity_type="supplier",
        entity_id=str(supplier_id),
        details=f"Поставщик #{supplier_id} переведен в архив / удален",
    )
    return {"status": "success", "message": f"Поставщик #{supplier_id} успешно архивирован / удален"}


@router.post("/{supplier_id}/offers", response_model=SupplierOfferResponse, status_code=status.HTTP_201_CREATED)
def add_or_update_offer(
    supplier_id: int,
    data: SupplierOfferCreate,
    organization_id: int = Depends(get_current_organization_id),
    user: User = Depends(require_roles(["owner", "manager"])),
    db: Session = Depends(get_db),
):
    sup = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.organization_id == organization_id
    ).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    prod = db.query(Product).filter(
        Product.id == data.product_id,
        Product.organization_id == organization_id
    ).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Check if offer already exists for this supplier and product
    existing_offer = db.query(SupplierOffer).filter(
        SupplierOffer.organization_id == organization_id,
        SupplierOffer.supplier_id == supplier_id,
        SupplierOffer.product_id == data.product_id,
    ).first()

    now = datetime.utcnow()
    new_price = round(abs(data.offered_price), 2)

    if existing_offer:
        old_price = existing_offer.offered_price
        if abs(old_price - new_price) > 0.01:
            change_pct = round(((new_price - old_price) / old_price) * 100, 1) if old_price > 0 else 0.0
            history_entry = OfferPriceHistory(
                organization_id=organization_id,
                offer_id=existing_offer.id,
                product_id=data.product_id,
                supplier_id=supplier_id,
                old_price=old_price,
                new_price=new_price,
                change_percent=change_pct,
                changed_at=now,
            )
            db.add(history_entry)

        existing_offer.offered_price = new_price
        existing_offer.unit = data.unit.strip() if data.unit else prod.unit
        existing_offer.package_quantity = data.package_quantity or 1.0
        existing_offer.minimum_order_quantity = data.minimum_order_quantity or 1.0
        existing_offer.delivery_cost = max(0.0, data.delivery_cost)
        existing_offer.valid_until = data.valid_until
        existing_offer.updated_at = now
        existing_offer.is_active = True
        db.commit()
        db.refresh(existing_offer)
        target_offer = existing_offer
    else:
        new_offer = SupplierOffer(
            organization_id=organization_id,
            product_id=data.product_id,
            supplier_id=supplier_id,
            offered_price=new_price,
            unit=data.unit.strip() if data.unit else prod.unit,
            package_quantity=data.package_quantity or 1.0,
            minimum_order_quantity=data.minimum_order_quantity or 1.0,
            delivery_cost=max(0.0, data.delivery_cost),
            valid_until=data.valid_until,
            updated_at=now,
            source_type="manual",
            is_demo=False,
            is_active=True,
        )
        db.add(new_offer)
        db.commit()
        db.refresh(new_offer)
        target_offer = new_offer

    log_activity(
        db=db,
        organization_id=organization_id,
        user=user,
        action="update_offer",
        entity_type="supplier_offer",
        entity_id=str(target_offer.id),
        details=f"Прайс поставщика {sup.name} для {prod.name}: {new_price} ₸/{target_offer.unit}",
    )

    return SupplierOfferResponse(
        id=target_offer.id,
        organization_id=target_offer.organization_id,
        product_id=target_offer.product_id,
        supplier_id=target_offer.supplier_id,
        supplier_name=sup.name,
        offered_price=target_offer.offered_price,
        unit=target_offer.unit,
        package_quantity=target_offer.package_quantity,
        minimum_order_quantity=target_offer.minimum_order_quantity,
        delivery_cost=target_offer.delivery_cost,
        valid_until=target_offer.valid_until,
        updated_at=target_offer.updated_at,
        is_demo=target_offer.is_demo,
        is_active=target_offer.is_active,
    )


@router.get("/price-history/all", response_model=List[PriceHistoryItemResponse])
def get_price_history(
    product_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    query = db.query(OfferPriceHistory).join(Supplier).filter(
        OfferPriceHistory.organization_id == organization_id
    )
    if product_id:
        query = query.filter(OfferPriceHistory.product_id == product_id)
    if supplier_id:
        query = query.filter(OfferPriceHistory.supplier_id == supplier_id)

    records = query.order_by(desc(OfferPriceHistory.changed_at)).limit(100).all()
    results = []
    for r in records:
        results.append(
            PriceHistoryItemResponse(
                id=r.id,
                product_id=r.product_id,
                supplier_id=r.supplier_id,
                supplier_name=r.supplier.name,
                old_price=r.old_price,
                new_price=r.new_price,
                change_percent=r.change_percent,
                changed_at=r.changed_at,
            )
        )
    return results
