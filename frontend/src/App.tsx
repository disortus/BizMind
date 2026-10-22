import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { AddTransactionModal } from './components/AddTransactionModal';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { FinancesPage } from './pages/FinancesPage';
import { PurchasesPage } from './pages/PurchasesPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { ForecastPage } from './pages/ForecastPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { ImportSettingsPage } from './pages/ImportSettingsPage';
import { OrdersPage } from './pages/OrdersPage';
import { InventoryPage } from './pages/InventoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { ReportBuilderPage } from './pages/ReportBuilderPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { api } from './services/api';
import { User, OrganizationInfo } from './types';

const VALID_TABS = [
  'dashboard',
  'finances',
  'purchases',
  'comparison',
  'forecast',
  'notifications',
  'import',
  'orders',
  'inventory',
  'reports',
  'settings',
];

const getTabFromPath = (path: string): { tab: string; isNotFound: boolean } => {
  const clean = path.replace(/^\/+|\/+$/g, '').toLowerCase();
  if (!clean || clean === 'dashboard') {
    return { tab: 'dashboard', isNotFound: false };
  }
  if (VALID_TABS.includes(clean)) {
    return { tab: clean, isNotFound: false };
  }
  return { tab: '404', isNotFound: true };
};

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [organizations, setOrganizations] = useState<OrganizationInfo[]>([]);
  const [currentOrgId, setCurrentOrgId] = useState<number>(api.getActiveOrgId());
  const [loading, setLoading] = useState(true);

  // Initialize active tab from current URL pathname
  const [activeTab, setActiveTab] = useState<string>(() => {
    const { tab } = getTabFromPath(window.location.pathname);
    return tab;
  });
  const [currentPath, setCurrentPath] = useState<string>(window.location.pathname);
  const [comparisonQuantity, setComparisonQuantity] = useState<number | null>(null);
  const [orderPreFill, setOrderPreFill] = useState<{
    supplierId?: number;
    productId?: number;
    quantity?: number;
    unitPrice?: number;
  } | null>(null);

  const [period, setPeriod] = useState<string>('30d');
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Synchronize browser history and popstate
  useEffect(() => {
    const handlePopState = () => {
      const { tab } = getTabFromPath(window.location.pathname);
      setActiveTab(tab);
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Check login state and load available organizations on initial mount
  useEffect(() => {
    const initAuth = async () => {
      if (!api.hasSavedOrg()) {
        try {
          const orgs = await api.getOrganizations();
          setOrganizations(orgs);
        } catch {
          // ignore
        } finally {
          setLoading(false);
        }
        return;
      }

      try {
        const [orgs, u] = await Promise.all([
          api.getOrganizations().catch(() => []),
          api.getMe().catch(() => null),
        ]);
        setOrganizations(orgs);

        if (u) {
          setUser(u);
          if (u.organization?.id) {
            setCurrentOrgId(u.organization.id);
          }
        } else {
          // Graceful reload recovery: attempt demoLogin with the active saved org
          const activeOrg = api.getActiveOrgId();
          const recoveredUser = await api.demoLogin(activeOrg).catch(() => null);
          if (recoveredUser) {
            setUser(recoveredUser);
            if (recoveredUser.organization?.id) {
              setCurrentOrgId(recoveredUser.organization.id);
            }
          } else {
            api.logout();
          }
        }
      } catch (e) {
        console.error('Auth initialization error:', e);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const handleReturnToCases = () => {
    api.logout();
    setUser(null);
    setSelectedProductId(null);
    setActiveTab('dashboard');
    setCurrentPath('/');
    window.history.pushState(null, '', '/');
    setIsMobileMenuOpen(false);
    api.getOrganizations().then(setOrganizations).catch(() => {});
  };

  // Fetch categories and unread notifications count whenever user, org, or refreshKey changes
  const refreshAuxData = async () => {
    try {
      const [cats, notifs] = await Promise.all([
        api.getCategories(),
        api.getNotifications(true),
      ]);
      setCategories(cats);
      setUnreadCount(notifs.length);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (user) {
      refreshAuxData();
    }
  }, [user, currentOrgId, refreshKey]);

  const handleNavigate = (
    tab: string,
    productId?: number,
    initialQty?: number,
    orderPreFillData?: {
      supplierId?: number;
      productId?: number;
      quantity?: number;
      unitPrice?: number;
    }
  ) => {
    if (productId !== undefined) {
      setSelectedProductId(productId);
    }
    if (initialQty !== undefined) {
      setComparisonQuantity(initialQty);
    }
    if (orderPreFillData) {
      setOrderPreFill(orderPreFillData);
    }
    setActiveTab(tab);
    const newPath = tab === 'dashboard' ? '/' : `/${tab}`;
    setCurrentPath(newPath);
    setIsMobileMenuOpen(false);
    window.history.pushState(null, '', newPath);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDataChanged = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleSwitchOrg = async (newOrgId: number) => {
    try {
      setLoading(true);
      const switchedUser = await api.switchOrganization(newOrgId);
      setCurrentOrgId(newOrgId);
      setUser(switchedUser);
      setSelectedProductId(null);
      setIsMobileMenuOpen(false);
      // Increment refreshKey to clear and reload state on all screens
      setRefreshKey((prev) => prev + 1);
    } catch (err) {
      console.error('Failed to switch organization', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0F17] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
          <div className="text-xs text-slate-400">Инициализация BizMind...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <LoginPage
        onLoginSuccess={(u) => {
          setUser(u);
          if (u.organization?.id) {
            setCurrentOrgId(u.organization.id);
          }
          api.getOrganizations().then(setOrganizations).catch(() => {});
        }}
      />
    );
  }

  const currentOrgMeta = organizations.find((o) => o.id === currentOrgId) || {
    id: currentOrgId,
    name: user.organization?.name || (currentOrgId === 1 ? 'Cafe Aroma' : 'Daily Cup'),
    scenario_title: currentOrgId === 1 ? 'Первоначальное внедрение' : 'Регулярное использование',
    demo_badge: currentOrgId === 1 ? 'Первоначальное внедрение' : 'Регулярное использование',
  };

  const getPageInfo = () => {
    const orgLabel = currentOrgMeta.name;
    switch (activeTab) {
      case 'dashboard':
        return {
          title: 'Сводный дашборд',
          subtitle: `Финансовое состояние и операционный контроль ${orgLabel}`,
        };
      case 'finances':
        return {
          title: 'Финансы и ДДС',
          subtitle: 'Учет доходов, операционных расходов и контроль кассовых разрывов',
        };
      case 'purchases':
        return {
          title: 'Закупки и динамика цен',
          subtitle: 'Анализ закупочных цен, динамика инфляции сырья и журнал поставок',
        };
      case 'comparison':
        return {
          title: 'Сравнение поставщиков',
          subtitle: 'Сопоставление цен, поиск выгодных условий и калькулятор объема партий',
        };
      case 'forecast':
        return {
          title: 'Прогноз кассовых разрывов',
          subtitle: 'Моделирование остатков денег на 30 дней с учетом платежей поставщикам',
        };
      case 'notifications':
        return {
          title: 'Центр уведомлений',
          subtitle: 'Системные алерты о росте цен, кассовых разрывах и дефиците остатков',
        };
      case 'import':
        return {
          title: 'Импорт и загрузка данных',
          subtitle: 'Загрузка финансовых выписок, прайс-листов поставщиков и накладных Excel / CSV',
        };
      case 'orders':
        return {
          title: 'Заказы поставщикам',
          subtitle: 'Оформление поставок, отслеживание статусов и складская приемка',
        };
      case 'inventory':
        return {
          title: 'Складской учет',
          subtitle: 'Учет фактических остатков сырья, инвентаризация и аудит списаний',
        };
      case 'reports':
        return {
          title: 'Шаблоны отчётов',
          subtitle: 'Конструктор аналитических отчетов, интерактивный аудит и выгрузка в Excel / CSV',
        };
      case 'settings':
        return {
          title: 'Настройки и администрирование',
          subtitle: 'Реквизиты организации, ролевой доступ и журнал аудита безопасности',
        };
      case '404':
        return {
          title: 'Страница не найдена',
          subtitle: 'Ошибка 404 — запрошенный раздел не найден',
        };
      default:
        return {
          title: 'BizMind',
          subtitle: 'Управление закупками и финансами',
        };
    }
  };

  const pageInfo = getPageInfo();

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex relative overflow-x-hidden">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab === '404' ? 'dashboard' : activeTab}
        onSelectTab={(tab) => {
          setSelectedProductId(null);
          handleNavigate(tab);
        }}
        unreadCount={unreadCount}
        user={user}
        currentOrgId={currentOrgId}
        organizations={organizations}
        onSwitchOrg={handleSwitchOrg}
        onReturnToCases={handleReturnToCases}
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar
          title={pageInfo.title}
          subtitle={pageInfo.subtitle}
          period={period}
          onPeriodChange={(p) => setPeriod(p)}
          onOpenAddModal={() => setIsAddModalOpen(true)}
          onResetDemo={() => handleNavigate('import')}
          onOpenNotifications={() => handleNavigate('notifications')}
          unreadCount={unreadCount}
          currentOrgName={currentOrgMeta.name}
          scenarioTitle={currentOrgMeta.scenario_title}
          onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
        />

        <main className="flex-1 pb-16">
          {activeTab === 'dashboard' && (
            <DashboardPage
              key={`dash-${currentOrgId}-${refreshKey}-${period}`}
              period={period}
              onNavigate={handleNavigate}
            />
          )}

          {activeTab === 'finances' && (
            <FinancesPage
              key={`fin-${currentOrgId}-${refreshKey}`}
              onOpenAddModal={() => setIsAddModalOpen(true)}
            />
          )}

          {activeTab === 'purchases' && (
            <PurchasesPage
              key={`purch-${currentOrgId}-${refreshKey}`}
              initialProductId={selectedProductId}
              onGoToComparison={(pid) => handleNavigate('comparison', pid)}
            />
          )}

          {activeTab === 'comparison' && (
            <ComparisonPage
              key={`comp-${currentOrgId}-${selectedProductId}-${refreshKey}`}
              selectedProductId={selectedProductId}
              initialQuantity={comparisonQuantity}
              onGoToOrder={(supplierId, productId, quantity, unitPrice) => {
                handleNavigate('orders', undefined, undefined, {
                  supplierId,
                  productId,
                  quantity,
                  unitPrice,
                });
              }}
            />
          )}

          {activeTab === 'forecast' && (
            <ForecastPage
              key={`fore-${currentOrgId}-${refreshKey}`}
              onGoToComparison={(pid) => handleNavigate('comparison', pid)}
            />
          )}

          {activeTab === 'notifications' && (
            <NotificationsPage
              key={`notif-${currentOrgId}-${refreshKey}`}
              onNavigate={handleNavigate}
              onRefreshUnread={refreshAuxData}
            />
          )}

          {activeTab === 'import' && (
            <ImportSettingsPage
              key={`import-${currentOrgId}-${refreshKey}`}
              onDataImported={handleDataChanged}
            />
          )}

          {activeTab === 'orders' && (
            <OrdersPage
              key={`ord-${currentOrgId}-${refreshKey}`}
              onRefreshAux={refreshAuxData}
              prefillOrder={orderPreFill}
              onClearPrefill={() => setOrderPreFill(null)}
            />
          )}

          {activeTab === 'inventory' && (
            <InventoryPage
              key={`inv-${currentOrgId}-${refreshKey}`}
            />
          )}

          {activeTab === 'reports' && (
            <ReportBuilderPage
              key={`rep-${currentOrgId}-${refreshKey}`}
              onNavigateToImport={() => handleNavigate('import')}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsPage
              key={`set-${currentOrgId}-${refreshKey}`}
              currentUser={user}
            />
          )}

          {activeTab === '404' && (
            <NotFoundPage
              currentPath={currentPath}
              onNavigate={handleNavigate}
              onReturnToCases={handleReturnToCases}
            />
          )}
        </main>
      </div>

      {/* Add Transaction Modal */}
      <AddTransactionModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={() => {
          handleDataChanged();
          refreshAuxData();
        }}
        categories={
          categories.length > 0
            ? categories.filter((c) => c !== 'Все')
            : [
                'Закупка кофе',
                'Закупка молока и продуктов',
                'Расходные материалы',
                'Аренда помещения',
                'Фонд оплаты труда',
                'Коммунальные услуги',
              ]
        }
      />
    </div>
  );
}

export default App;
