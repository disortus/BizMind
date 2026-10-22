from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.models import Product, InventoryMovement
from backend.schemas.schemas import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    def get_products(
        db: Session,
        organization_id: int = 1,
        category: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        include_archived: bool = False,
    ) -> List[Product]:
        query = db.query(Product).filter(Product.organization_id == organization_id)

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        elif not include_archived:
            query = query.filter(Product.is_active == True)

        if category and category != "Все":
            query = query.filter(Product.category == category)

        if search:
            search_pat = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_pat)) | (Product.sku.ilike(search_pat))
            )

        return query.order_by(Product.category.asc(), Product.name.asc()).all()

    @staticmethod
    def get_product(
        db: Session,
        product_id: int,
        organization_id: int = 1,
    ) -> Optional[Product]:
        return db.query(Product).filter(
            Product.id == product_id,
            Product.organization_id == organization_id,
        ).first()

    @staticmethod
    def create_product(
        db: Session,
        data: ProductCreate,
        organization_id: int = 1,
    ) -> Product:
        prod = Product(
            organization_id=organization_id,
            name=data.name.strip(),
            sku=data.sku.strip() if data.sku else None,
            category=data.category.strip(),
            unit=data.unit.strip(),
            unit_ratio=data.unit_ratio or 1.0,
            package_quantity=data.package_quantity or 1.0,
            package_unit=data.package_unit.strip() if data.package_unit else data.unit.strip(),
            current_stock=max(0.0, data.current_stock),
            minimum_stock=max(0.0, data.minimum_stock),
            description=data.description.strip() if data.description else None,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(prod)
        db.flush()

        # If initial stock > 0, record initial stock inventory movement
        if prod.current_stock > 0:
            init_move = InventoryMovement(
                organization_id=organization_id,
                product_id=prod.id,
                movement_type="initial_stock",
                quantity=prod.current_stock,
                unit=prod.unit,
                previous_stock=0.0,
                resulting_stock=prod.current_stock,
                reason="Первоначальный ввод остатка при создании товара",
                created_at=datetime.utcnow(),
            )
            db.add(init_move)

        db.commit()
        db.refresh(prod)
        return prod

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        data: ProductUpdate,
        organization_id: int = 1,
    ) -> Optional[Product]:
        prod = db.query(Product).filter(
            Product.id == product_id,
            Product.organization_id == organization_id,
        ).first()
        if not prod:
            return None

        if data.name is not None:
            prod.name = data.name.strip()
        if data.sku is not None:
            prod.sku = data.sku.strip()
        if data.category is not None:
            prod.category = data.category.strip()
        if data.unit is not None:
            prod.unit = data.unit.strip()
        if data.unit_ratio is not None:
            prod.unit_ratio = data.unit_ratio
        if data.package_quantity is not None:
            prod.package_quantity = data.package_quantity
        if data.package_unit is not None:
            prod.package_unit = data.package_unit.strip()
        if data.minimum_stock is not None:
            prod.minimum_stock = max(0.0, data.minimum_stock)
        if data.description is not None:
            prod.description = data.description.strip()
        if data.is_active is not None:
            prod.is_active = data.is_active

        db.commit()
        db.refresh(prod)
        return prod

    @staticmethod
    def delete_product(
        db: Session,
        product_id: int,
        organization_id: int = 1,
        hard_delete: bool = False,
    ) -> bool:
        prod = db.query(Product).filter(
            Product.id == product_id,
            Product.organization_id == organization_id,
        ).first()
        if not prod:
            return False

        if hard_delete:
            db.delete(prod)
        else:
            prod.is_active = False

        db.commit()
        return True

    @staticmethod
    def get_categories(db: Session, organization_id: int = 1) -> List[str]:
        results = (
            db.query(Product.category)
            .filter(Product.organization_id == organization_id)
            .distinct()
            .order_by(Product.category.asc())
            .all()
        )
        return [r[0] for r in results if r[0]]
