import React from 'react';
import {
  LayoutDashboard,
  Wallet,
  ShoppingBag,
  ArrowLeftRight,
  TrendingUp,
  Bell,
  FileSpreadsheet,
  Coffee,
  Sparkles,
} from 'lucide-react';
import { cn } from '../utils/formatters';

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  unreadCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  unreadCount,
}) => {
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

  return (
    <aside className="w-64 bg-[#0F172A] border-r border-[#1E293B] flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-[#1E293B]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Sparkles className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                BizMind
                <span className="text-[10px] uppercase font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded">
                  MVP
                </span>
              </div>
              <p className="text-xs text-slate-400">Финансы & Закупки</p>
            </div>
          </div>

          {/* Organization Badge */}
          <div className="mt-4 p-2.5 rounded-lg bg-[#161F30] border border-[#243045] flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
              <Coffee className="w-4 h-4 text-amber-400" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-semibold text-white truncate">
                Cafe Aroma
              </div>
              <div className="text-[11px] text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Демонстрация
              </div>
            </div>
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
                onClick={() => onSelectTab(item.id)}
                className={cn(
                  'w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#161F30]'
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon className={cn('w-4 h-4', isActive ? 'text-emerald-400' : 'text-slate-400')} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={cn(
                      'text-[11px] font-semibold px-2 py-0.5 rounded-full',
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
      <div className="p-4 border-t border-[#1E293B] bg-[#0B0F17]/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
              АС
            </div>
            <div className="text-left">
              <div className="text-xs font-semibold text-slate-200">Алексей Смирнов</div>
              <div className="text-[11px] text-slate-500">Управляющий</div>
            </div>
          </div>
        </div>
        <div className="mt-3 text-[10px] text-slate-500 text-center">
          BizMind v1.0 • Спец-проект для жюри
        </div>
      </div>
    </aside>
  );
};
