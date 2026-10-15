import React from 'react';
import {
  Calendar,
  Plus,
  RotateCcw,
  Bell,
  Sparkles,
  Menu,
} from 'lucide-react';
import { cn } from '../utils/formatters';

interface NavbarProps {
  title: string;
  subtitle: string;
  period: string;
  onPeriodChange: (p: string) => void;
  onOpenAddModal: () => void;
  onResetDemo: () => void;
  onOpenNotifications: () => void;
  unreadCount: number;
  currentOrgName: string;
  scenarioTitle: string;
  onOpenMobileMenu?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  title,
  subtitle,
  period,
  onPeriodChange,
  onOpenAddModal,
  onResetDemo,
  onOpenNotifications,
  unreadCount,
  currentOrgName,
  scenarioTitle,
  onOpenMobileMenu,
}) => {
  const periods = [
    { id: '30d', label: '30 дней' },
    { id: '90d', label: '90 дней' },
    { id: 'month', label: 'Октябрь 2026' },
    { id: 'all', label: 'Все время' },
  ];

  return (
    <header className="h-16 px-3 sm:px-6 border-b border-[#1E293B] bg-[#0F172A]/80 backdrop-blur-md sticky top-0 z-20 flex items-center justify-between gap-2">
      {/* Title & Organization Context */}
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        {/* Mobile Hamburger Button */}
        {onOpenMobileMenu && (
          <button
            onClick={onOpenMobileMenu}
            className="p-2 -ml-1 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition lg:hidden shrink-0"
            aria-label="Открыть навигационное меню"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="min-w-0">
          <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
            <h1 className="text-sm sm:text-base font-bold text-white tracking-tight truncate">
              {title}
            </h1>
            <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
              <span className="text-[9px] sm:text-[10px] font-semibold px-1.5 sm:px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                {currentOrgName}
              </span>
              <span className="hidden sm:inline-flex text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300">
                {scenarioTitle}
              </span>
              <span className="hidden xl:inline-flex text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                Демонстрационные данные
              </span>
            </div>
          </div>
          <p className="hidden md:block text-xs text-slate-400 truncate">{subtitle}</p>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
        {/* Desktop Period Selector Pills */}
        <div className="hidden sm:flex items-center bg-[#161F30] p-1 rounded-lg border border-[#243045]">
          <Calendar className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1" />
          {periods.map((p) => {
            const active = period === p.id;
            return (
              <button
                key={p.id}
                onClick={() => onPeriodChange(p.id)}
                className={cn(
                  'px-2 py-1 text-xs font-medium rounded-md transition-all',
                  active
                    ? 'bg-emerald-500 text-slate-950 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                )}
              >
                {p.label}
              </button>
            );
          })}
        </div>

        {/* Mobile Period Selector (Compact Select) */}
        <div className="sm:hidden flex items-center bg-[#161F30] px-2 py-1.5 rounded-lg border border-[#243045]">
          <Calendar className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
          <select
            value={period}
            onChange={(e) => onPeriodChange(e.target.value)}
            className="bg-transparent text-emerald-400 font-semibold text-xs focus:outline-none cursor-pointer"
            aria-label="Выбор периода"
          >
            <option value="30d" className="bg-[#161F30] text-white">30 дней</option>
            <option value="90d" className="bg-[#161F30] text-white">90 дней</option>
            <option value="month" className="bg-[#161F30] text-white">Октябрь</option>
            <option value="all" className="bg-[#161F30] text-white">Все время</option>
          </select>
        </div>

        {/* Quick Add Operation */}
        <button
          onClick={onOpenAddModal}
          className="flex items-center gap-1 px-2.5 sm:px-3 py-1.5 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/25 text-xs font-semibold transition"
          title="Добавить финансовую операцию"
        >
          <Plus className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">+ Операция</span>
        </button>

        {/* Notification Bell */}
        <button
          onClick={onOpenNotifications}
          className="relative p-2 rounded-lg bg-[#161F30] border border-[#243045] text-slate-300 hover:text-white hover:border-slate-600 transition"
          title="Центр уведомлений"
          aria-label="Уведомления"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center">
              {unreadCount}
            </span>
          )}
        </button>

        {/* Reset Demo Button */}
        <button
          onClick={onResetDemo}
          className="flex items-center gap-1 px-2 sm:px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-slate-400 hover:text-amber-300 hover:border-amber-500/40 text-xs font-medium transition"
          title="Восстановить исходные демонстрационные данные"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Сброс демо</span>
        </button>
      </div>
    </header>
  );
};

