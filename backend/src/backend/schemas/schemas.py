from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


# -------------------------------------------------------------------------
# Auth & Organization
# -------------------------------------------------------------------------
class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    business_type: str
    currency: Optional[str] = "₸"
    alert_threshold_percent: Optional[float] = 5.0
    price_alert_threshold_percent: Optional[float] = None
    low_stock_days_threshold: Optional[int] = 5
    address: Optional[str] = None
    phone: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: Optional[datetime] = None

    @model_validator(mode="after")
    def populate_aliases(self):
        if self.price_alert_threshold_percent is None and self.alert_threshold_percent is not None:
            self.price_alert_threshold_percent = self.alert_threshold_percent
        elif self.alert_threshold_percent is None and self.price_alert_threshold_percent is not None:
            self.alert_threshold_percent = self.price_alert_threshold_percent
        if self.contact_phone is None:
            self.contact_phone = self.phone
        if self.phone is None:
            self.phone = self.contact_phone
        if self.contact_email is None:
            self.contact_email = self.email
        if self.email is None:
            self.email = self.contact_email
        return self


class OrganizationSettingsUpdate(BaseModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    currency: Optional[str] = None
    alert_threshold_percent: Optional[float] = None
    price_alert_threshold_percent: Optional[float] = None
    low_stock_days_threshold: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    contact_email: Optional[str] = None


class OrganizationInfo(BaseModel):
    id: int
    name: str
    business_type: str
    scenario_type: str  # "initial_adoption" | "regular_usage"
    scenario_title: str  # "Первоначальное внедрение" | "Регулярное использование"
    scenario_description: str
    demo_badge: str
    user_name: str
    user_email: str
    user_role: str
    created_at: datetime


class OrganizationSwitchRequest(BaseModel):
    organization_id: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    name: str
    email: str
    role: str
    is_active: Optional[bool] = True
    created_at: datetime
    organization: Optional[OrganizationResponse] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserCreateRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "manager"  # owner, manager, employee


# -------------------------------------------------------------------------
# Financials
# -------------------------------------------------------------------------
class TransactionCreate(BaseModel):
    transaction_date: date
    description: str
    category: str
    amount: float
    transaction_type: str = "expense"  # expense | income
    payment_method: str = "cashless"  # cashless, cash, card
    source: str = "manual"
    supplier_id: Optional[int] = None
    purchase_order_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: Optional[str] = None
    payment_method: Optional[str] = None
    supplier_id: Optional[int] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    transaction_date: date
    description: str
    category: str
    amount: float
    transaction_type: str
    payment_method: Optional[str] = "cashless"
    source: str
    supplier_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    import_batch_id: Optional[int] = None
    is_archived: Optional[bool] = False
    created_at: datetime


class FinanceSummary(BaseModel):
    total_expenses: float
    total_income: float
    net_profit: float
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    categories_breakdown: List[Dict[str, Any]]


# -------------------------------------------------------------------------
# Products & Catalog
# -------------------------------------------------------------------------
class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    category: str
    unit: str = "шт"
    unit_ratio: float = 1.0
    package_quantity: float = 1.0
    package_unit: str = "шт"
    current_stock: float = 0.0
    minimum_stock: float = 0.0
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    unit_ratio: Optional[float] = None
    package_quantity: Optional[float] = None
    package_unit: Optional[str] = None
    minimum_stock: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    name: str
    sku: Optional[str] = None
    category: str
    unit: str
    unit_ratio: Optional[float] = 1.0
    package_quantity: float
    package_unit: str
    current_stock: float
    minimum_stock: float
    description: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: datetime


# -------------------------------------------------------------------------
# Suppliers & Offers
# -------------------------------------------------------------------------
class SupplierCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    delivery_cost: float = 0.0
    minimum_order_amount: float = 0.0
    source_type: str = "manual"


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    delivery_cost: Optional[float] = None
    minimum_order_amount: Optional[float] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: Optional[int] = None
    name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    delivery_cost: float
    minimum_order_amount: float
    source_type: str = "imported"  # global, imported, manual
    is_global: bool = False
    is_demo: bool
    is_active: Optional[bool] = True


class SupplierOfferCreate(BaseModel):
    product_id: int
    supplier_id: Optional[int] = None
    offered_price: float
    unit: str = "шт"
    package_quantity: float = 1.0
    minimum_order_quantity: float = 1.0
    delivery_cost: float = 0.0
    valid_until: Optional[date] = None
    price_source: str = "catalog"  # catalog, user_import, manual


class SupplierOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: Optional[int] = None
    product_id: int
    supplier_id: int
    supplier_name: Optional[str] = None
    offered_price: float
    unit: str
    package_quantity: float
    minimum_order_quantity: float
    delivery_cost: float
    valid_until: Optional[date] = None
    updated_at: datetime
    source_type: Optional[str] = "mock"
    price_source: str = "catalog"  # catalog, user_import, manual
    is_demo: bool
    is_active: bool = True


class PriceHistoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    supplier_id: int
    supplier_name: str
    old_price: float
    new_price: float
    change_percent: float
    changed_at: datetime


class SupplierCatalogItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    category: Optional[str] = None
    unit: str
    unit_price: float
    package_quantity: float = 1.0
    minimum_order_quantity: float = 1.0
    price_source: str = "catalog"
    is_global: bool = False
    notes: Optional[str] = None


# -------------------------------------------------------------------------
# Purchases & Orders (Procurement Workflow)
# -------------------------------------------------------------------------
class PurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    product_category: str
    supplier_id: int
    supplier_name: str
    purchase_date: date
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    source: str


class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    ordered_quantity: Optional[float] = None
    quantity: Optional[float] = None
    unit_price: float
    unit: Optional[str] = None

    @model_validator(mode="after")
    def resolve_item_quantity(self):
        if self.ordered_quantity is None and self.quantity is not None:
            self.ordered_quantity = float(self.quantity)
        if self.quantity is None and self.ordered_quantity is not None:
            self.quantity = float(self.ordered_quantity)
        if self.ordered_quantity is None or self.ordered_quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        return self


class PurchaseOrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    purchase_order_id: int
    product_id: int
    product_name: str
    ordered_quantity: float
    received_quantity: Optional[float] = None
    unit: str
    unit_price: float
    total_price: float


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    items: List[PurchaseOrderItemCreate]
    delivery_cost: float = 0.0
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_default_order_date(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("order_date"):
                data["order_date"] = date.today()
        return data


class PurchaseOrderUpdate(BaseModel):
    status: Optional[str] = None  # draft, confirmed, cancelled
    supplier_id: Optional[int] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    delivery_cost: Optional[float] = None
    notes: Optional[str] = None
    items: Optional[List[PurchaseOrderItemCreate]] = None


class PurchaseOrderReceiveRequest(BaseModel):
    # Optional map of {item_id: actual_received_quantity}
    received_quantities: Optional[Dict[int, float]] = None
    items: Optional[List[Dict[str, Any]]] = None
    record_financial_expense: bool = True
    payment_method: str = "cashless"


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    order_number: str
    supplier_id: int
    supplier_name: str
    order_date: date
    status: str
    subtotal_amount: float
    delivery_cost: float
    total_amount: float
    notes: Optional[str] = None
    created_by_name: Optional[str] = None
    received_at: Optional[datetime] = None
    created_at: datetime
    items: List[PurchaseOrderItemResponse] = []


class PriceHistoryPoint(BaseModel):
    date: date
    price: float
    supplier_name: str
    quantity: float


class ProductPriceHistoryResponse(BaseModel):
    product_id: int
    product_name: str
    unit: str
    current_price: float
    previous_price: Optional[float] = None
    price_change_percent: Optional[float] = None
    history: List[PriceHistoryPoint]


# -------------------------------------------------------------------------
# Inventory Movements & Stock
# -------------------------------------------------------------------------
class InventoryMovementCreate(BaseModel):
    product_id: int
    movement_type: str  # receipt, write_off, adjustment
    quantity: float  # positive
    reason: str
    reference_id: Optional[str] = None


class StockAdjustmentRequest(BaseModel):
    product_id: int
    actual_stock: float
    reason: str = "Инвентаризация"


class InventoryMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    product_id: int
    product_name: str
    movement_type: str
    quantity: float
    unit: str
    previous_stock: float
    resulting_stock: float
    reason: str
    reference_id: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime


# -------------------------------------------------------------------------
# Comparison & Offers
# -------------------------------------------------------------------------
class AlternativeOfferItem(BaseModel):
    supplier_id: int
    supplier_name: str
    supplier_source_type: str = "imported"  # global, imported, manual
    price_source: str = "catalog"  # catalog, user_import, manual
    is_global_supplier: bool = False
    offered_price: float
    unit: str
    package_quantity: float
    minimum_order_quantity: float
    delivery_cost: float
    unit_difference: float
    total_difference: float
    total_difference_with_delivery: float
    updated_at: datetime
    is_better: bool
    is_demo: bool
    is_stale: bool = False
    warning_note: Optional[str] = None


class PriceComparisonResponse(BaseModel):
    product_id: int
    product_name: str
    unit: str
    current_supplier_id: Optional[int]
    current_supplier_name: Optional[str]
    current_unit_price: float
    previous_unit_price: Optional[float]
    price_change_percent: Optional[float]
    selected_quantity: float
    alternative_offers: List[AlternativeOfferItem]
    best_offer: Optional[AlternativeOfferItem] = None
    formula_note: str


# -------------------------------------------------------------------------
# Forecast
# -------------------------------------------------------------------------
class ForecastItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    unit: str
    current_stock: float
    minimum_stock: float
    avg_daily_consumption: float
    days_left: Optional[float]
    forecast_7d: float
    forecast_14d: float
    forecast_30d: float
    recommended_order_quantity: float
    status: str  # critical, low, normal, insufficient_data
    calculation_method: str = "Moving Average (90d)"
    note: str


class ForecastSummary(BaseModel):
    total_products_tracked: int
    critical_items_count: int
    low_stock_items_count: int
    items: List[ForecastItem]


# -------------------------------------------------------------------------
# Notifications
# -------------------------------------------------------------------------
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    severity: str
    notification_type: str
    related_product_id: Optional[int] = None
    is_read: bool
    created_at: datetime


# -------------------------------------------------------------------------
# Dashboard
# -------------------------------------------------------------------------
class CategoryExpense(BaseModel):
    category: str
    amount: float
    percentage: float


class ExpenseDynamicPoint(BaseModel):
    date: str
    amount: float
    income: Optional[float] = 0.0


class DashboardSummary(BaseModel):
    period: str
    total_expenses: float
    previous_period_expenses: float
    expenses_change_percent: float
    total_income: float
    active_suppliers_count: int
    potential_savings_monthly: float
    pending_alerts_count: int
    categories: List[CategoryExpense]
    dynamics: List[ExpenseDynamicPoint]
    recent_purchases: List[PurchaseResponse]
    top_price_alerts: List[NotificationResponse]
    featured_comparison: Optional[PriceComparisonResponse] = None
    is_empty: bool = False
    onboarding_steps: List[str] = []


# -------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------
class ImportBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    import_type: str
    status: str
    rows_total: int
    rows_imported: int
    rows_skipped: int
    error_summary: Optional[str] = None
    created_at: datetime


class ImportPreviewResult(BaseModel):
    file_name: str
    import_type: str
    headers_detected: List[str]
    sample_rows: List[Dict[str, Any]]
    total_rows: int
    is_valid: bool
    message: str


class ImportExecuteResult(BaseModel):
    batch_id: int
    file_name: str
    import_type: str
    status: str
    rows_total: int
    rows_imported: int
    rows_skipped: int
    message: str
    errors: List[str] = []


# -------------------------------------------------------------------------
# Activity Log
# -------------------------------------------------------------------------
class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime


# -------------------------------------------------------------------------
# Report Builder & Templates
# -------------------------------------------------------------------------
class ReportTemplateConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: Optional[str] = None
    sections: List[str] = ["kpi_summary", "detailed_table"]
    period_type: str = "current_month"  # current_month, previous_month, last_30d, last_90d, custom
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_by: Optional[str] = "category"  # day, week, month, category, supplier
    sort_by: Optional[str] = "amount_desc"
    filters: Optional[Dict[str, Any]] = None


class ReportTemplateCreate(BaseModel):
    title: str
    description: Optional[str] = None
    report_type: str  # financial, procurement, inventory, executive
    config: ReportTemplateConfig


class ReportTemplateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    report_type: Optional[str] = None
    config: Optional[ReportTemplateConfig] = None
    is_archived: Optional[bool] = None


class ReportTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    report_type: str
    config: Dict[str, Any]
    is_system: bool
    is_archived: bool
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ReportPreviewRequest(BaseModel):
    report_type: str
    config: ReportTemplateConfig


class ReportPreviewResponse(BaseModel):
    title: str
    report_type: str
    organization_name: str
    currency: str
    period_label: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    generated_at: datetime
    kpi_cards: List[Dict[str, Any]] = []
    charts: Dict[str, Any] = {}
    summary_data: List[Dict[str, Any]] = []
    columns: List[Dict[str, str]] = []
    rows: List[Dict[str, Any]] = []
    is_empty: bool = False
    message: Optional[str] = None

