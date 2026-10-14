from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.deps import get_current_organization_id
from backend.models.models import Supplier
from backend.schemas.schemas import SupplierResponse, PriceComparisonResponse
from backend.services.comparison_service import ComparisonService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.get("", response_model=List[SupplierResponse])
def get_suppliers(
    organization_id: int = Depends(get_current_organization_id),
    db: Session = Depends(get_db)
):
    return db.query(Supplier).filter(
        Supplier.organization_id == organization_id
    ).order_by(Supplier.name.asc()).all()

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
