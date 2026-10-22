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
    currency = Column(String(20), default="₸")
    alert_threshold_percent = Column(Float, default=5.0)
    address = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organization", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="organization", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="organization", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="organization", cascade="all, delete-orphan")
    supplier_offers = relationship("SupplierOffer", back_populates="organization", cascade="all, delete-orphan")
    transactions = relationship("FinancialTransaction", back_populates="organization", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="organization", cascade="all, delete-orphan")
    import_batches = relationship("ImportBatch", back_populates="organization", cascade="all, delete-orphan")
    inventory_movements = relationship("InventoryMovement", back_populates="organization", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="organization", cascade="all, delete-orphan")
    report_templates = relationship("ReportTemplate", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), default="owner")  # owner, manager, employee
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    purchase_orders = relationship("PurchaseOrder", back_populates="created_by_user")
    inventory_movements = relationship("InventoryMovement", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    report_templates = relationship("ReportTemplate", back_populates="created_by_user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(50), nullable=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    unit = Column(String(50), nullable=False, default="шт")
    unit_ratio = Column(Float, default=1.0)
    package_quantity = Column(Float, default=1.0)
    package_unit = Column(String(50), default="шт")
    current_stock = Column(Float, default=0.0)
    minimum_stock = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="products")
    purchases = relationship("Purchase", back_populates="product", cascade="all, delete-orphan")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product", cascade="all, delete-orphan")
    offers = relationship("SupplierOffer", back_populates="product", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product", cascade="all, delete-orphan")
    price_history = relationship("OfferPriceHistory", back_populates="product", cascade="all, delete-orphan")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    delivery_cost = Column(Float, default=0.0)
    minimum_order_amount = Column(Float, default=0.0)
    source_type = Column(String(50), default="imported")  # global, imported, manual
    is_global = Column(Boolean, default=False)
    is_demo = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="suppliers")
    purchases = relationship("Purchase", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    offers = relationship("SupplierOffer", back_populates="supplier", cascade="all, delete-orphan")
    price_history = relationship("OfferPriceHistory", back_populates="supplier", cascade="all, delete-orphan")
    transactions = relationship("FinancialTransaction", back_populates="supplier")


class SupplierOffer(Base):
    __tablename__ = "supplier_offers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    offered_price = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    package_quantity = Column(Float, default=1.0)
    minimum_order_quantity = Column(Float, default=1.0)
    delivery_cost = Column(Float, default=0.0)
    valid_until = Column(Date, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String(50), default="mock")
    price_source = Column(String(50), default="catalog")  # catalog, user_import, manual
    is_demo = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="supplier_offers")
    product = relationship("Product", back_populates="offers")
    supplier = relationship("Supplier", back_populates="offers")
    price_history = relationship("OfferPriceHistory", back_populates="offer", cascade="all, delete-orphan")


class OfferPriceHistory(Base):
    __tablename__ = "offer_price_history"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    offer_id = Column(Integer, ForeignKey("supplier_offers.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    change_percent = Column(Float, default=0.0)
    changed_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_history")
    supplier = relationship("Supplier", back_populates="price_history")
    offer = relationship("SupplierOffer", back_populates="price_history")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    order_number = Column(String(50), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    order_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="draft")  # draft, confirmed, received, cancelled
    subtotal_amount = Column(Float, default=0.0)
    delivery_cost = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="purchase_orders")
    supplier = relationship("Supplier", back_populates="purchase_orders")
    created_by_user = relationship("User", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    transactions = relationship("FinancialTransaction", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    ordered_quantity = Column(Float, nullable=False)
    received_quantity = Column(Float, nullable=True)
    unit = Column(String(50), nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="purchase_order_items")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(30), nullable=False)  # receipt, write_off, adjustment, initial_stock
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    previous_stock = Column(Float, default=0.0)
    resulting_stock = Column(Float, default=0.0)
    reason = Column(String(255), nullable=False)
    reference_id = Column(String(100), nullable=True)  # e.g. PO-2026-001
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="inventory_movements")
    product = relationship("Product", back_populates="inventory_movements")
    user = relationship("User", back_populates="inventory_movements")


class Purchase(Base):
    """
    Legacy flat purchase record preserved for backward compatibility and fast reporting.
    """
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
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    import_batch = relationship("ImportBatch", back_populates="purchases")


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    description = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False, default="expense")  # expense or income
    payment_method = Column(String(50), default="cashless")  # cashless, cash, card
    source = Column(String(50), default="manual")
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True)
    import_batch_id = Column(Integer, ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="transactions")
    supplier = relationship("Supplier", back_populates="transactions")
    purchase_order = relationship("PurchaseOrder", back_populates="transactions")
    import_batch = relationship("ImportBatch", back_populates="transactions")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # warning, info, danger, success
    notification_type = Column(String(50), nullable=False)  # price_spike, alternative_offer, low_stock, expense_change, stale_price, purchase_pending
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


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_name = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="activity_logs")
    user = relationship("User", back_populates="activity_logs")


class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # financial, procurement, inventory, executive
    config = Column(Text, nullable=False)  # JSON-encoded configuration
    is_system = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="report_templates")
    created_by_user = relationship("User", back_populates="report_templates")

