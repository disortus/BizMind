from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from backend.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    business_type = Column(String(100), default="Кофейня")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organization", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="organization", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="organization", cascade="all, delete-orphan")
    supplier_offers = relationship("SupplierOffer", back_populates="organization", cascade="all, delete-orphan")
    transactions = relationship("FinancialTransaction", back_populates="organization", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="organization", cascade="all, delete-orphan")
    import_batches = relationship("ImportBatch", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(100), default="Управляющий")
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    unit = Column(String(50), nullable=False, default="шт")
    package_quantity = Column(Float, default=1.0)
    package_unit = Column(String(50), default="шт")
    current_stock = Column(Float, default=0.0)
    minimum_stock = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="products")
    purchases = relationship("Purchase", back_populates="product", cascade="all, delete-orphan")
    offers = relationship("SupplierOffer", back_populates="product", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="product")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=True)
    delivery_cost = Column(Float, default=0.0)
    minimum_order_amount = Column(Float, default=0.0)
    source_type = Column(String(50), default="manual")
    is_demo = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="suppliers")
    purchases = relationship("Purchase", back_populates="supplier")
    offers = relationship("SupplierOffer", back_populates="supplier", cascade="all, delete-orphan")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    purchase_date = Column(Date, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    source = Column(String(50), default="legacy_import")
    import_batch_id = Column(Integer, ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    import_batch = relationship("ImportBatch", back_populates="purchases")


class SupplierOffer(Base):
    __tablename__ = "supplier_offers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    offered_price = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    package_quantity = Column(Float, default=1.0)
    minimum_order_quantity = Column(Float, default=1.0)
    delivery_cost = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String(50), default="mock")
    is_demo = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="supplier_offers")
    product = relationship("Product", back_populates="offers")
    supplier = relationship("Supplier", back_populates="offers")


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    description = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False, default="expense")  # expense or income
    source = Column(String(50), default="legacy_import")
    import_batch_id = Column(Integer, ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="transactions")
    import_batch = relationship("ImportBatch", back_populates="transactions")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # warning, info, danger, success
    notification_type = Column(String(50), nullable=False)  # price_spike, alternative_offer, low_stock, expense_change
    related_product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="notifications")
    product = relationship("Product", back_populates="notifications")


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    import_type = Column(String(50), nullable=False)  # finances, purchases, inventory, supplier_prices
    status = Column(String(20), default="success")  # success, partial, failed
    rows_total = Column(Integer, default=0)
    rows_imported = Column(Integer, default=0)
    rows_skipped = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="import_batches")
    transactions = relationship("FinancialTransaction", back_populates="import_batch")
    purchases = relationship("Purchase", back_populates="import_batch")
