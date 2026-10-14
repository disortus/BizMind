from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Auth & Organization
# -------------------------------------------------------------------------
class OrganizationResponse(BaseModel):
    id: int
    name: str
    business_type: str
    created_at: datetime

    class Config:
        from_attributes = True


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
    id: int
    name: str
    email: str
    role: str
    organization: OrganizationResponse

    class Config:
        from_attributes = True


# -------------------------------------------------------------------------
# Financials
# -------------------------------------------------------------------------
class TransactionCreate(BaseModel):
    transaction_date: date
    description: str
    category: str
    amount: float
    transaction_type: str = "expense"  # expense | income
    source: str = "manual"


class TransactionResponse(BaseModel):
    id: int
    organization_id: int
    transaction_date: date
    description: str
    category: str
    amount: float
    transaction_type: str
    source: str
    import_batch_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FinanceSummary(BaseModel):
    total_expenses: float
    total_income: float
    net_profit: float
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    categories_breakdown: List[Dict[str, Any]]


# -------------------------------------------------------------------------
# Products & Suppliers
# -------------------------------------------------------------------------
class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    unit: str
    package_quantity: float
    package_unit: str
    current_stock: float
    minimum_stock: float

    class Config:
        from_attributes = True


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_name: Optional[str] = None
    delivery_cost: float
    minimum_order_amount: float
    source_type: str
    is_demo: bool

    class Config:
        from_attributes = True


# -------------------------------------------------------------------------
# Purchases
# -------------------------------------------------------------------------
class PurchaseResponse(BaseModel):
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

    class Config:
        from_attributes = True


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
# Comparison & Offers
# -------------------------------------------------------------------------
class AlternativeOfferItem(BaseModel):
    supplier_id: int
    supplier_name: str
    offered_price: float
    unit: str
    package_quantity: float
    minimum_order_quantity: float
    delivery_cost: float
    unit_difference: float  # (current_price - offered_price)
    total_difference: float  # for given quantity
    total_difference_with_delivery: float
    updated_at: datetime
    is_better: bool
    is_demo: bool


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
    status: str  # critical, low, normal
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
    id: int
    title: str
    description: str
    severity: str
    notification_type: str
    related_product_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


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


# -------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------
class ImportBatchResponse(BaseModel):
    id: int
    file_name: str
    import_type: str
    status: str
    rows_total: int
    rows_imported: int
    rows_skipped: int
    error_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


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
