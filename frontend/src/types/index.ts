export interface Organization {
  id: number;
  name: string;
  business_type: string;
  created_at: string;
}

export interface OrganizationInfo {
  id: number;
  name: string;
  business_type: string;
  scenario_type: 'initial_adoption' | 'regular_usage';
  scenario_title: string;
  scenario_description: string;
  demo_badge: string;
  user_name: string;
  user_email: string;
  user_role: string;
  created_at: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  organization: Organization;
}

export interface FinancialTransaction {
  id: number;
  organization_id: number;
  transaction_date: string;
  description: string;
  category: string;
  amount: number;
  transaction_type: 'expense' | 'income';
  source: string;
  import_batch_id?: number | null;
  created_at: string;
}

export interface FinanceSummary {
  total_expenses: number;
  total_income: number;
  net_profit: number;
  period_start?: string | null;
  period_end?: string | null;
  categories_breakdown: {
    category: string;
    amount: number;
    percentage: number;
  }[];
}

export interface Product {
  id: number;
  name: string;
  category: string;
  unit: string;
  sku?: string | null;
  description?: string | null;
  package_quantity: number;
  package_unit: string;
  current_stock: number;
  minimum_stock: number;
  is_active?: boolean;
}

export interface Supplier {
  id: number;
  organization_id?: number | null;
  name: string;
  contact_name?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  notes?: string | null;
  delivery_cost: number;
  minimum_order_amount: number;
  source_type: 'global' | 'imported' | 'manual' | string;
  is_global: boolean;
  is_demo: boolean;
  is_active?: boolean;
}

export interface Purchase {
  id: number;
  product_id: number;
  product_name: string;
  product_category: string;
  supplier_id: number;
  supplier_name: string;
  purchase_date: string;
  quantity: number;
  unit: string;
  unit_price: number;
  total_price: number;
  source: string;
}

export interface PriceHistoryPoint {
  date: string;
  price: number;
  supplier_name: string;
  quantity: number;
}

export interface ProductPriceHistory {
  product_id: number;
  product_name: string;
  unit: string;
  current_price: number;
  previous_price?: number | null;
  price_change_percent?: number | null;
  history: PriceHistoryPoint[];
}

export interface AlternativeOfferItem {
  supplier_id: number;
  supplier_name: string;
  supplier_source_type?: 'global' | 'imported' | 'manual' | string;
  price_source?: 'catalog' | 'user_import' | 'manual' | string;
  is_global_supplier?: boolean;
  offered_price: number;
  unit: string;
  package_quantity: number;
  minimum_order_quantity: number;
  delivery_cost: number;
  unit_difference: number;
  total_difference: number;
  total_difference_with_delivery: number;
  updated_at: string;
  is_better: boolean;
  is_demo: boolean;
  is_stale?: boolean;
  warning_note?: string | null;
}

export interface PriceComparison {
  product_id: number;
  product_name: string;
  unit: string;
  current_supplier_id?: number | null;
  current_supplier_name?: string | null;
  current_unit_price: number;
  previous_unit_price?: number | null;
  price_change_percent?: number | null;
  selected_quantity: number;
  alternative_offers: AlternativeOfferItem[];
  best_offer?: AlternativeOfferItem | null;
  formula_note: string;
}

export interface ForecastItem {
  product_id: number;
  product_name: string;
  category: string;
  unit: string;
  current_stock: number;
  minimum_stock: number;
  avg_daily_consumption: number;
  days_left?: number | null;
  forecast_7d: number;
  forecast_14d: number;
  forecast_30d: number;
  recommended_order_quantity: number;
  status: 'critical' | 'low' | 'normal';
  note: string;
}

export interface ForecastSummary {
  total_products_tracked: number;
  critical_items_count: number;
  low_stock_items_count: number;
  items: ForecastItem[];
}

export interface NotificationItem {
  id: number;
  title: string;
  description: string;
  severity: 'warning' | 'info' | 'danger' | 'success';
  notification_type: 'price_spike' | 'alternative_offer' | 'low_stock' | 'expense_change';
  related_product_id?: number | null;
  is_read: boolean;
  created_at: string;
}

export interface CategoryExpense {
  category: string;
  amount: number;
  percentage: number;
}

export interface ExpenseDynamicPoint {
  date: string;
  amount: number;
  income?: number;
}

export interface DashboardSummary {
  period: string;
  total_expenses: number;
  previous_period_expenses: number;
  expenses_change_percent: number;
  total_income: number;
  active_suppliers_count: number;
  potential_savings_monthly: number;
  pending_alerts_count: number;
  categories: CategoryExpense[];
  dynamics: ExpenseDynamicPoint[];
  recent_purchases: Purchase[];
  top_price_alerts: NotificationItem[];
  featured_comparison?: PriceComparison | null;
  is_empty?: boolean;
  empty_reason?: string | null;
  onboarding_steps?: Array<{
    step: number;
    title: string;
    description: string;
    done: boolean;
    link: string;
    import_type?: string;
  }>;
}

export interface ImportBatch {
  id: number;
  file_name: string;
  import_type: string;
  status: 'success' | 'partial' | 'failed' | 'processing';
  rows_total: number;
  rows_imported: number;
  rows_skipped: number;
  error_summary?: string | null;
  created_at: string;
}

export interface ImportPreviewResult {
  file_name: string;
  import_type: string;
  headers_detected: string[];
  sample_rows: Record<string, any>[];
  total_rows: number;
  is_valid: boolean;
  message: string;
}

export interface ImportExecuteResult {
  batch_id: number;
  file_name: string;
  import_type: string;
  status: string;
  rows_total: number;
  rows_imported: number;
  rows_skipped: number;
  message: string;
  errors: string[];
}

export interface SampleFileInfo {
  filename: string;
  name: string;
  import_type: string;
  description: string;
  size: string;
}

export interface PurchaseOrderItem {
  id?: number;
  product_id: number;
  product_name?: string;
  quantity: number;
  received_quantity?: number | null;
  unit: string;
  unit_price: number;
  total_price: number;
}

export interface PurchaseOrder {
  id: number;
  organization_id: number;
  order_number: string;
  supplier_id: number;
  supplier_name: string;
  order_date: string;
  expected_delivery_date?: string | null;
  received_date?: string | null;
  status: 'draft' | 'confirmed' | 'received' | 'cancelled';
  subtotal_amount: number;
  delivery_cost: number;
  total_amount: number;
  notes?: string | null;
  created_by_user_id?: number | null;
  created_at: string;
  items: PurchaseOrderItem[];
}

export interface CreatePurchaseOrderData {
  supplier_id: number;
  order_date: string;
  expected_delivery_date?: string | null;
  delivery_cost?: number;
  notes?: string | null;
  items: {
    product_id: number;
    quantity: number;
    unit_price: number;
  }[];
}

export interface InventoryMovement {
  id: number;
  organization_id: number;
  product_id: number;
  product_name: string;
  movement_type: 'initial' | 'receipt' | 'write_off' | 'adjustment';
  quantity: number;
  stock_after: number;
  reason?: string | null;
  reference_id?: number | null;
  created_by_user_id?: number | null;
  created_at: string;
}

export interface StockAdjustmentData {
  product_id: number;
  actual_stock: number;
  reason?: string;
}

export interface WriteOffData {
  product_id: number;
  quantity: number;
  reason: string;
}

export interface OrganizationSettings {
  id: number;
  name: string;
  business_type: string;
  currency: string;
  price_alert_threshold_percent: number;
  low_stock_days_threshold: number;
  contact_email?: string | null;
  contact_phone?: string | null;
  address?: string | null;
}

export interface ActivityLogItem {
  id: number;
  created_at: string;
  user_name: string;
  action: string;
  entity_type: string;
  entity_id?: number | null;
  details?: Record<string, any> | null;
}

export interface CreateUserData {
  email: string;
  name: string;
  role: string;
  password?: string;
}

// ----------------------------------------------------------------------------
// Report Builder & Templates
// ----------------------------------------------------------------------------
export interface ReportTemplateConfig {
  title?: string;
  sections: string[];
  period_type: 'current_month' | 'previous_month' | 'last_30d' | 'last_90d' | 'custom' | string;
  start_date?: string | null;
  end_date?: string | null;
  group_by?: 'day' | 'week' | 'month' | 'category' | 'supplier' | string;
  sort_by?: 'amount_desc' | 'amount_asc' | 'date_desc' | 'date_asc' | 'stock_asc' | string;
  filters?: Record<string, any> | null;
}

export interface ReportTemplate {
  id: number;
  organization_id?: number | null;
  title: string;
  description?: string | null;
  report_type: 'financial' | 'procurement' | 'inventory' | 'executive';
  config: ReportTemplateConfig;
  is_system: boolean;
  is_archived: boolean;
  created_by_user_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface ReportTemplateCreate {
  title: string;
  description?: string;
  report_type: 'financial' | 'procurement' | 'inventory' | 'executive';
  config: ReportTemplateConfig;
}

export interface ReportTemplateUpdate {
  title?: string;
  description?: string;
  report_type?: 'financial' | 'procurement' | 'inventory' | 'executive';
  config?: ReportTemplateConfig;
  is_archived?: boolean;
}

export interface ReportKPICard {
  title: string;
  value: string;
  subtitle: string;
  badge?: string;
  type?: 'income' | 'expense' | 'profit' | 'loss' | 'neutral' | 'savings';
}

export interface ReportPreviewResponse {
  title: string;
  report_type: string;
  organization_name: string;
  currency: string;
  period_label: string;
  start_date?: string | null;
  end_date?: string | null;
  generated_at: string;
  kpi_cards: ReportKPICard[];
  charts: Record<string, any>;
  summary_data: any[];
  columns: Array<{ key: string; label: string }>;
  rows: Record<string, any>[];
  is_empty: boolean;
  message?: string | null;
}


