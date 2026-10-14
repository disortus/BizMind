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
import { api } from './services/api';
import { User, OrganizationInfo } from './types';

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [organizations, setOrganizations] = useState<OrganizationInfo[]>([]);
  const [currentOrgId, setCurrentOrgId] = useState<number>(api.getActiveOrgId());
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [period, setPeriod] = useState<string>('30d');
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [refreshKey, setRefreshKey] = useState(0);

  // Check login state and load available organizations on initial mount
  useEffect(() => {
    Promise.all([
      api.getOrganizations().catch(() => []),
      api.getMe().catch(() => null),
    ])
      .then(([orgs, u]) => {
        setOrganizations(orgs);
        if (u) {
          setUser(u);
          if (u.organization?.id) {
            setCurrentOrgId(u.organization.id);
          }
        }
      })
      .finally(() => setLoading(false));
  }, []);

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

  const handleNavigate = (tab: string, productId?: number) => {
    if (productId !== undefined) {
      setSelectedProductId(productId);
    }
    setActiveTab(tab);
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
          title: 'Финансовые операции',
          subtitle: `Журнал доходов и расходов предприятия ${orgLabel} за выбранный период`,
        };
      case 'purchases':
        return {
          title: 'История закупок',
          subtitle: 'Детализация партий сырья, упаковки и динамика цен',
        };
      case 'comparison':
        return {
          title: 'Сравнение цен поставщиков',
          subtitle: 'Сопоставление прайс-листов и оценка потенциальной разницы',
        };
      case 'forecast':
        return {
          title: 'Прогноз остатков и потребности',
          subtitle: 'Статистический расчет расхода сырья и рекомендации к заказу',
        };
      case 'notifications':
        return {
          title: 'Центр уведомлений',
          subtitle: 'Сигналы о скачках цен, неснижаемых остатках и динамике бюджета',
        };
      case 'import':
        return {
          title: 'Импорт и управление данными',
          subtitle: `Загрузка внешних таблиц Excel/CSV и управление базой ${orgLabel}`,
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
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setSelectedProductId(null);
          setActiveTab(tab);
        }}
        unreadCount={unreadCount}
        user={user}
        currentOrgId={currentOrgId}
        organizations={organizations}
        onSwitchOrg={handleSwitchOrg}
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
