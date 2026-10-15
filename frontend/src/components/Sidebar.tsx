import React, { useState } from 'react';
import {
  LayoutDashboard,
  Wallet,
  ShoppingBag,
  ArrowLeftRight,
  TrendingUp,
  Bell,
  FileSpreadsheet,
  Coffee,
  Store,
  Sparkles,
  ChevronDown,
  Check,
  LogOut,
  ArrowLeft,
  X,
} from 'lucide-react';
import { cn } from '../utils/formatters';
import { User, OrganizationInfo } from '../types';

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  unreadCount: number;
  user: User | null;
  currentOrgId: number;
  organizations: OrganizationInfo[];
  onSwitchOrg: (orgId: number) => void;
  onReturnToCases?: () => void;
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  unreadCount,
  user,
  currentOrgId,
  organizations,
  onSwitchOrg,
  onReturnToCases,
  isMobileOpen = false,
  onCloseMobile,
}) => {
  const [isOrgDropdownOpen, setIsOrgDropdownOpen] = useState(false);

  const navItems = [
    {
      id: 'dashboard',
      label: 'Дашборд',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      id: 'finances',
      label: 'Финансы',
      icon: Wallet,
      badge: null,
    },
    {
      id: 'purchases',
      label: 'Закупки',
      icon: ShoppingBag,
      badge: null,
    },
    {
      id: 'comparison',
      label: 'Сравнение цен',
      icon: ArrowLeftRight,
      badge: 'Выгода',
    },
    {
      id: 'forecast',
      label: 'Прогноз остатков',
      icon: TrendingUp,
      badge: null,
    },
    {
      id: 'notifications',
      label: 'Уведомления',
      icon: Bell,
      badge: unreadCount > 0 ? String(unreadCount) : null,
    },
    {
      id: 'import',
      label: 'Импорт и данные',
      icon: FileSpreadsheet,
      badge: null,
    },
  ];

  const currentOrg = organizations.find((o) => o.id === currentOrgId) || {
    id: currentOrgId,
    name: user?.organization?.name || (currentOrgId === 1 ? 'Cafe Aroma' : 'Daily Cup'),
    scenario_title: currentOrgId === 1 ? 'Первоначальное внедрение' : 'Регулярное использование',
    demo_badge: currentOrgId === 1 ? 'Первоначальное внедрение' : 'Регулярное использование',
  };

  const getUserInitials = (name?: string) => {
    if (!name) return 'БМ';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  const handleTabClick = (tabId: string) => {
    onSelectTab(tabId);
    if (onCloseMobile) {
      onCloseMobile();
    }
  };

  const renderContent = (isMobile: boolean = false) => (
    <>
      <div className="flex-1 overflow-y-auto">
        {/* Brand Header */}
        <div className="p-4 border-b border-[#1E293B]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <Sparkles className="w-5 h-5 text-slate-950 font-bold" />
              </div>
              <div>
                <div className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
                  BizMind
                  <span className="text-[10px] uppercase font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1 py-0.2 rounded">
                    SaaS
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">Финансы & Закупки</p>
              </div>
            </div>

            {/* Mobile close button */}
            {isMobile && onCloseMobile && (
              <button
                onClick={onCloseMobile}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition lg:hidden"
                aria-label="Закрыть меню"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Interactive Organization Switcher */}
          <div className="relative mt-3">
            <button
              onClick={() => setIsOrgDropdownOpen((prev) => !prev)}
              className="w-full p-2.5 rounded-xl bg-[#161F30] border border-[#243045] hover:border-emerald-500/40 text-left transition flex items-center justify-between group"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <div className={cn(
                  'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border',
                  currentOrgId === 1
                    ? 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                    : 'bg-teal-500/10 border-teal-500/20 text-teal-400'
                )}>
                  {currentOrgId === 1 ? <Coffee className="w-4 h-4" /> : <Store className="w-4 h-4" />}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-bold text-white truncate flex items-center gap-1">
                    {currentOrg.name}
                  </div>
                  <div className="text-[10px] text-emerald-400 font-medium truncate">
                    {currentOrg.scenario_title}
                  </div>
                </div>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-200 transition shrink-0 ml-1" />
            </button>

            {/* Dropdown Menu */}
            {isOrgDropdownOpen && (
              <div className="absolute top-full left-0 right-0 mt-1.5 p-1.5 rounded-xl bg-[#161F30] border border-[#243045] shadow-2xl z-50 space-y-1">
                <div className="px-2 py-1 text-[10px] uppercase tracking-wider text-slate-400 font-bold border-b border-[#243045]/60 mb-1">
                  Демонстрационные пространства
                </div>
                {[
                  { id: 1, name: 'Cafe Aroma', subtitle: 'Первоначальное внедрение', icon: Coffee, color: 'text-amber-400' },
                  { id: 2, name: 'Daily Cup', subtitle: 'Регулярное использование', icon: Store, color: 'text-teal-400' },
                ].map((item) => {
                  const Icon = item.icon;
                  const isSelected = currentOrgId === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        setIsOrgDropdownOpen(false);
                        if (currentOrgId !== item.id) {
                          onSwitchOrg(item.id);
                        }
                        if (isMobile && onCloseMobile) {
                          onCloseMobile();
                        }
                      }}
                      className={cn(
                        'w-full flex items-center justify-between p-2 rounded-lg text-left text-xs transition',
                        isSelected
                          ? 'bg-emerald-500/15 border border-emerald-500/30 text-white font-semibold'
                          : 'text-slate-300 hover:bg-[#1E293B] hover:text-white'
                      )}
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <Icon className={cn('w-4 h-4 shrink-0', item.color)} />
                        <div className="min-w-0">
                          <div className="truncate font-semibold">{item.name}</div>
                          <div className="text-[10px] text-slate-400 truncate">{item.subtitle}</div>
                        </div>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 ml-2" />}
                    </button>
                  );
                })}
                {onReturnToCases && (
                  <button
                    onClick={() => {
                      setIsOrgDropdownOpen(false);
                      onReturnToCases();
                      if (isMobile && onCloseMobile) {
                        onCloseMobile();
                      }
                    }}
                    className="w-full flex items-center gap-2 p-2 rounded-lg text-left text-xs text-slate-400 hover:text-emerald-300 hover:bg-[#1E293B] border-t border-[#243045]/60 transition mt-1"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    <span>К выбору кейса</span>
                  </button>
                )}
                <div className="px-2 pt-1 text-[9px] text-slate-500 text-center border-t border-[#243045]/60">
                  Демо-данные изолированы
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleTabClick(item.id)}
                className={cn(
                  'w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all duration-150',
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25 shadow-sm font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#161F30]'
                )}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={cn('w-4 h-4', isActive ? 'text-emerald-400' : 'text-slate-400')} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={cn(
                      'text-[10px] font-semibold px-1.5 py-0.2 rounded-full',
                      item.id === 'notifications'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer User Info */}
      <div className="p-3.5 border-t border-[#1E293B] bg-[#0B0F17]/50 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300 shrink-0">
              {getUserInitials(user?.name)}
            </div>
            <div className="text-left min-w-0">
              <div className="text-xs font-semibold text-slate-200 truncate">
                {user?.name || 'Пользователь'}
              </div>
              <div className="text-[10px] text-slate-400 truncate">
                {user?.role || 'Управляющий'}
              </div>
            </div>
          </div>
          {onReturnToCases && (
            <button
              onClick={() => {
                onReturnToCases();
                if (isMobile && onCloseMobile) {
                  onCloseMobile();
                }
              }}
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 transition"
              title="Выйти к экрану выбора кейсов"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
        <div className="mt-2.5 pt-2 border-t border-[#1E293B]/60 text-[10px] text-slate-500 flex items-center justify-between">
          <span>BizMind v1.0</span>
          <span className="text-emerald-400/80 font-medium">Демо-режим</span>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar (Unchanged layout for lg+ screens) */}
      <aside className="hidden lg:flex w-64 bg-[#0F172A] border-r border-[#1E293B] flex-col justify-between shrink-0 h-screen sticky top-0">
        {renderContent(false)}
      </aside>

      {/* Mobile Backdrop Overlay */}
      <div
        className={cn(
          'fixed inset-0 bg-slate-950/75 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300',
          isMobileOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        )}
        onClick={onCloseMobile}
        aria-hidden="true"
      />

      {/* Mobile Drawer */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-[#0F172A] border-r border-[#1E293B] flex flex-col justify-between transform transition-transform duration-300 ease-in-out lg:hidden shadow-2xl',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        aria-label="Мобильная навигация"
      >
        {renderContent(true)}
      </aside>
    </>
  );
};

