import axios from 'axios';
import {
  User,
  OrganizationInfo,
  DashboardSummary,
  FinancialTransaction,
  FinanceSummary,
  Product,
  Purchase,
  ProductPriceHistory,
  Supplier,
  PriceComparison,
  ForecastSummary,
  NotificationItem,
  ImportBatch,
  ImportPreviewResult,
  ImportExecuteResult,
  SampleFileInfo,
  PurchaseOrder,
  CreatePurchaseOrderData,
  InventoryMovement,
  StockAdjustmentData,
  WriteOffData,
  OrganizationSettings,
  ActivityLogItem,
  CreateUserData,
  ReportTemplate,
  ReportTemplateConfig,
  ReportTemplateCreate,
  ReportTemplateUpdate,
  ReportPreviewResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach the active organization header dynamically
client.interceptors.request.use((config) => {
  const orgId = localStorage.getItem('bizmind_org_id');
  if (orgId) {
    config.headers['X-Organization-Id'] = orgId;
  }
  return config;
});

export const api = {
  // Auth & Organizations
  getOrganizations: async (): Promise<OrganizationInfo[]> => {
    const res = await client.get<OrganizationInfo[]>('/auth/organizations');
    return res.data;
  },
  demoLogin: async (orgId?: number): Promise<User> => {
    if (orgId) {
      localStorage.setItem('bizmind_org_id', String(orgId));
    }
    const targetOrg = orgId || Number(localStorage.getItem('bizmind_org_id') || '1');
    const res = await client.post<User>(`/auth/demo-login?org_id=${targetOrg}`);
    if (res.data?.organization?.id) {
      localStorage.setItem('bizmind_org_id', String(res.data.organization.id));
    }
    return res.data;
  },
  switchOrganization: async (organizationId: number): Promise<User> => {
    localStorage.setItem('bizmind_org_id', String(organizationId));
    const res = await client.post<User>('/auth/switch-org', { organization_id: organizationId });
    return res.data;
  },
  getActiveOrgId: (): number => {
    return Number(localStorage.getItem('bizmind_org_id') || '1');
  },
  hasSavedOrg: (): boolean => {
    return Boolean(localStorage.getItem('bizmind_org_id'));
  },
  logout: (): void => {
    localStorage.removeItem('bizmind_org_id');
  },
  getMe: async (): Promise<User> => {
    const res = await client.get<User>('/auth/me');
    return res.data;
  },

  // Dashboard
  getDashboard: async (period = '30d'): Promise<DashboardSummary> => {
    const res = await client.get<DashboardSummary>(`/dashboard?period=${period}`);
    return res.data;
  },

  // Finances
  getFinances: async (params?: {
    category?: string;
    transaction_type?: string;
    search?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<FinancialTransaction[]> => {
    const res = await client.get<FinancialTransaction[]>('/finances', { params });
    return res.data;
  },
  createTransaction: async (data: {
    transaction_date: string;
    description: string;
    category: string;
    amount: number;
    transaction_type: string;
  }): Promise<FinancialTransaction> => {
    const res = await client.post<FinancialTransaction>('/finances', data);
    return res.data;
  },
  updateTransaction: async (
    id: number,
    data: {
      transaction_date?: string;
      description?: string;
      category?: string;
      amount?: number;
      transaction_type?: string;
    }
  ): Promise<FinancialTransaction> => {
    const res = await client.put<FinancialTransaction>(`/finances/${id}`, data);
    return res.data;
  },
  deleteTransaction: async (id: number): Promise<{ message: string }> => {
    const res = await client.delete<{ message: string }>(`/finances/${id}`);
    return res.data;
  },
  getFinanceSummary: async (params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<FinanceSummary> => {
    const res = await client.get<FinanceSummary>('/finances/summary', { params });
    return res.data;
  },
  getCategories: async (): Promise<string[]> => {
    const res = await client.get<string[]>('/finances/categories');
    return res.data;
  },
  getFinancesExportUrl: (format: 'excel' | 'csv' = 'excel', params?: { start_date?: string; end_date?: string }): string => {
    const base = import.meta.env.VITE_API_URL || '/api';
    const query = new URLSearchParams({ format });
    if (params?.start_date) query.append('start_date', params.start_date);
    if (params?.end_date) query.append('end_date', params.end_date);
    const orgId = localStorage.getItem('bizmind_org_id') || '1';
    return `${base}/finances/export?${query.toString()}&org_id=${orgId}`;
  },

  // Products
  getProducts: async (params?: { search?: string; category?: string; include_archived?: boolean }): Promise<Product[]> => {
    const res = await client.get<Product[]>('/products', { params });
    return res.data;
  },
  getProduct: async (id: number): Promise<Product> => {
    const res = await client.get<Product>(`/products/${id}`);
    return res.data;
  },
  createProduct: async (data: {
    name: string;
    category: string;
    unit: string;
    sku?: string;
    description?: string;
    package_quantity?: number;
    package_unit?: string;
    current_stock?: number;
    minimum_stock?: number;
  }): Promise<Product> => {
    const res = await client.post<Product>('/products', data);
    return res.data;
  },
  updateProduct: async (id: number, data: Partial<Product>): Promise<Product> => {
    const res = await client.put<Product>(`/products/${id}`, data);
    return res.data;
  },
  deleteProduct: async (id: number): Promise<{ message: string }> => {
    const res = await client.delete<{ message: string }>(`/products/${id}`);
    return res.data;
  },
  getProductHistory: async (productId: number): Promise<ProductPriceHistory> => {
    const res = await client.get<ProductPriceHistory>(`/purchases/products/${productId}/history`);
    return res.data;
  },

  // Purchases
  getPurchases: async (params?: {
    product_id?: number;
    supplier_id?: number;
    search?: string;
  }): Promise<Purchase[]> => {
    const res = await client.get<Purchase[]>('/purchases', { params });
    return res.data;
  },

  // Purchase Orders
  getOrders: async (params?: {
    status?: string;
    supplier_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<PurchaseOrder[]> => {
    const res = await client.get<PurchaseOrder[]>('/orders', { params });
    return res.data;
  },
  getOrder: async (id: number): Promise<PurchaseOrder> => {
    const res = await client.get<PurchaseOrder>(`/orders/${id}`);
    return res.data;
  },
  createOrder: async (data: CreatePurchaseOrderData): Promise<PurchaseOrder> => {
    const res = await client.post<PurchaseOrder>('/orders', data);
    return res.data;
  },
  updateOrder: async (id: number, data: Partial<CreatePurchaseOrderData>): Promise<PurchaseOrder> => {
    const res = await client.put<PurchaseOrder>(`/orders/${id}`, data);
    return res.data;
  },
  confirmOrder: async (id: number): Promise<PurchaseOrder> => {
    const res = await client.post<PurchaseOrder>(`/orders/${id}/confirm`);
    return res.data;
  },
  receiveOrder: async (
    id: number,
    items?: { product_id: number; quantity: number }[]
  ): Promise<PurchaseOrder> => {
    const res = await client.post<PurchaseOrder>(`/orders/${id}/receive`, { items });
    return res.data;
  },
  cancelOrder: async (id: number): Promise<PurchaseOrder> => {
    const res = await client.post<PurchaseOrder>(`/orders/${id}/cancel`);
    return res.data;
  },
  getOrderDocument: async (id: number): Promise<string> => {
    const res = await client.get<string>(`/orders/${id}/document`);
    return res.data;
  },

  // Inventory
  getInventoryMovements: async (params?: {
    product_id?: number;
    movement_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<InventoryMovement[]> => {
    const res = await client.get<InventoryMovement[]>('/inventory/movements', { params });
    return res.data;
  },
  adjustStock: async (data: StockAdjustmentData): Promise<InventoryMovement> => {
    const res = await client.post<InventoryMovement>('/inventory/adjust', data);
    return res.data;
  },
  writeOffStock: async (data: WriteOffData): Promise<InventoryMovement> => {
    const res = await client.post<InventoryMovement>('/inventory/write-off', data);
    return res.data;
  },
  getInventoryExportUrl: (format: 'excel' | 'csv' = 'excel'): string => {
    const base = import.meta.env.VITE_API_URL || '/api';
    const orgId = localStorage.getItem('bizmind_org_id') || '1';
    return `${base}/inventory/export?format=${format}&org_id=${orgId}`;
  },

  // Suppliers & Comparison
  getSuppliers: async (params?: { source_type?: string }): Promise<Supplier[]> => {
    const res = await client.get<Supplier[]>('/suppliers', { params });
    return res.data;
  },
  createSupplier: async (data: {
    name: string;
    contact_name?: string;
    phone?: string;
    email?: string;
    notes?: string;
    delivery_cost?: number;
    minimum_order_amount?: number;
  }): Promise<Supplier> => {
    const res = await client.post<Supplier>('/suppliers', data);
    return res.data;
  },
  updateSupplier: async (id: number, data: Partial<Supplier>): Promise<Supplier> => {
    const res = await client.put<Supplier>(`/suppliers/${id}`, data);
    return res.data;
  },
  deleteSupplier: async (id: number): Promise<{ message: string }> => {
    const res = await client.delete<{ message: string }>(`/suppliers/${id}`);
    return res.data;
  },
  getSupplierOffers: async (supplierId: number): Promise<any[]> => {
    const res = await client.get<any[]>(`/suppliers/${supplierId}/offers`);
    return res.data;
  },
  addSupplierOffer: async (
    supplierId: number,
    data: {
      product_id: number;
      offered_price: number;
      unit: string;
      package_quantity?: number;
      minimum_order_quantity?: number;
      is_available?: boolean;
    }
  ): Promise<any> => {
    const res = await client.post(`/suppliers/${supplierId}/offers`, data);
    return res.data;
  },
  comparePrices: async (productId: number, quantity: number): Promise<PriceComparison> => {
    const res = await client.get<PriceComparison>(
      `/suppliers/comparison?product_id=${productId}&quantity=${quantity}`
    );
    return res.data;
  },

  // Settings & Activity Logs
  getOrganizationSettings: async (): Promise<OrganizationSettings> => {
    const res = await client.get<OrganizationSettings>('/settings/organization');
    return res.data;
  },
  updateOrganizationSettings: async (
    data: Partial<OrganizationSettings>
  ): Promise<OrganizationSettings> => {
    const res = await client.put<OrganizationSettings>('/settings/organization', data);
    return res.data;
  },
  getUsers: async (): Promise<User[]> => {
    const res = await client.get<User[]>('/settings/users');
    return res.data;
  },
  createUser: async (data: CreateUserData): Promise<User> => {
    const res = await client.post<User>('/settings/users', data);
    return res.data;
  },
  getActivityLogs: async (params?: {
    limit?: number;
    offset?: number;
    action?: string;
  }): Promise<ActivityLogItem[]> => {
    const res = await client.get<ActivityLogItem[]>('/settings/activity', { params });
    return res.data;
  },

  // Forecast
  getForecast: async (): Promise<ForecastSummary> => {
    const res = await client.get<ForecastSummary>('/forecast');
    return res.data;
  },

  // Notifications
  getNotifications: async (unreadOnly = false): Promise<NotificationItem[]> => {
    const res = await client.get<NotificationItem[]>(
      `/notifications?unread_only=${unreadOnly}`
    );
    return res.data;
  },
  markNotificationRead: async (id: number): Promise<void> => {
    await client.post(`/notifications/${id}/read`);
  },
  markAllNotificationsRead: async (): Promise<void> => {
    await client.post('/notifications/read-all');
  },

  // Import
  previewImport: async (file: File, importType: string): Promise<ImportPreviewResult> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('import_type', importType);
    const res = await client.post<ImportPreviewResult>('/import/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  executeImport: async (file: File, importType: string): Promise<ImportExecuteResult> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('import_type', importType);
    const res = await client.post<ImportExecuteResult>('/import/execute', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  getImportBatches: async (): Promise<ImportBatch[]> => {
    const res = await client.get<ImportBatch[]>('/import/batches');
    return res.data;
  },
  getTemplateDownloadUrl: (importType: string, format: 'excel' | 'csv' = 'excel'): string => {
    const base = import.meta.env.VITE_API_URL || '/api';
    return `${base}/import/templates/${importType}?format=${format}`;
  },

  // Report Templates & Builder
  getReportTemplates: async (includeArchived = false): Promise<ReportTemplate[]> => {
    const res = await client.get<ReportTemplate[]>(`/reports/templates?include_archived=${includeArchived}`);
    return res.data;
  },
  getReportTemplate: async (id: number): Promise<ReportTemplate> => {
    const res = await client.get<ReportTemplate>(`/reports/templates/${id}`);
    return res.data;
  },
  createReportTemplate: async (data: ReportTemplateCreate): Promise<ReportTemplate> => {
    const res = await client.post<ReportTemplate>('/reports/templates', data);
    return res.data;
  },
  updateReportTemplate: async (id: number, data: ReportTemplateUpdate): Promise<ReportTemplate> => {
    const res = await client.put<ReportTemplate>(`/reports/templates/${id}`, data);
    return res.data;
  },
  duplicateReportTemplate: async (id: number): Promise<ReportTemplate> => {
    const res = await client.post<ReportTemplate>(`/reports/templates/${id}/duplicate`);
    return res.data;
  },
  deleteReportTemplate: async (id: number): Promise<{ message: string }> => {
    const res = await client.delete<{ message: string }>(`/reports/templates/${id}`);
    return res.data;
  },
  previewReport: async (payload: { report_type: string; config: ReportTemplateConfig }): Promise<ReportPreviewResponse> => {
    const res = await client.post<ReportPreviewResponse>('/reports/preview', payload);
    return res.data;
  },
  exportReportExcel: async (payload: { report_type: string; config: ReportTemplateConfig }): Promise<Blob> => {
    const res = await client.post('/reports/export/excel', payload, {
      responseType: 'blob',
    });
    return res.data;
  },
  exportReportCsv: async (payload: { report_type: string; config: ReportTemplateConfig }): Promise<Blob> => {
    const res = await client.post('/reports/export/csv', payload, {
      responseType: 'blob',
    });
    return res.data;
  },

  // Demo Controls
  resetDemo: async (): Promise<any> => {
    const res = await client.post('/demo/reset');
    return res.data;
  },
  getSampleFiles: async (): Promise<SampleFileInfo[]> => {
    const res = await client.get<SampleFileInfo[]>('/demo/sample-files');
    return res.data;
  },
  downloadSampleUrl: (filename: string): string => {
    const base = import.meta.env.VITE_API_URL || '/api';
    return `${base}/demo/files/${filename}`;
  },
};
