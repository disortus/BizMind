from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.models.models import Product
from backend.schemas.schemas import (
    PurchaseResponse,
    ProductResponse,
    ProductPriceHistoryResponse,
)
from backend.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.get("", response_model=List[PurchaseResponse])
def get_purchases(
    product_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(200, le=500),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    return PurchaseService.get_purchases(
        db=db,
        organization_id=organization_id,
        product_id=product_id,
        supplier_id=supplier_id,
        search=search,
        limit=limit,
    )

@router.get("/products", response_model=List[ProductResponse])
def get_products(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(
        Product.organization_id == organization_id
    ).order_by(Product.name.asc()).all()
    return products

@router.get("/products/{product_id}/history", response_model=ProductPriceHistoryResponse)
def get_product_price_history(
    product_id: int,
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    res = PurchaseService.get_product_price_history(
        db=db, product_id=product_id, organization_id=organization_id
    )
    if not res:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return res


@router.get("/comparison/{product_id}")
def compare_offers(
    product_id: int,
    quantity: float = Query(20.0, gt=0),
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
):
    from backend.services.comparison_service import ComparisonService
    comparison = ComparisonService.compare_product_offers(
        db=db, product_id=product_id, quantity=quantity, organization_id=organization_id
    )
    if not comparison:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return comparison

