export interface Organization {
  id: number;
  name: string;
  business_type: string;
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
  package_quantity: number;
  package_unit: string;
  current_stock: number;
  minimum_stock: number;
}

export interface Supplier {
  id: number;
  name: string;
  contact_name?: string | null;
  delivery_cost: number;
  minimum_order_amount: number;
  source_type: string;
  is_demo: boolean;
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
