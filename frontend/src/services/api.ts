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

  // Purchases
  getPurchases: async (params?: {
    product_id?: number;
    supplier_id?: number;
    search?: string;
  }): Promise<Purchase[]> => {
    const res = await client.get<Purchase[]>('/purchases', { params });
    return res.data;
  },
  getProducts: async (): Promise<Product[]> => {
    const res = await client.get<Product[]>('/purchases/products');
    return res.data;
  },
  getProductHistory: async (productId: number): Promise<ProductPriceHistory> => {
    const res = await client.get<ProductPriceHistory>(`/purchases/products/${productId}/history`);
    return res.data;
  },

  // Suppliers & Comparison
  getSuppliers: async (): Promise<Supplier[]> => {
    const res = await client.get<Supplier[]>('/suppliers');
    return res.data;
  },
  comparePrices: async (productId: number, quantity: number): Promise<PriceComparison> => {
    const res = await client.get<PriceComparison>(
      `/suppliers/comparison?product_id=${productId}&quantity=${quantity}`
    );
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
