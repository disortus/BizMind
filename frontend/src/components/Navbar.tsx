import React from 'react';
import {
  Calendar,
  Plus,
  RotateCcw,
  Bell,
  CheckCircle2,
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
}) => {
  const periods = [
    { id: '30d', label: '30 дней' },
    { id: '90d', label: '90 дней' },
    { id: 'month', label: 'Октябрь 2026' },
    { id: 'all', label: 'Все время' },
  ];

  return (
    <header className="h-16 px-8 border-b border-[#1E293B] bg-[#0F172A]/80 backdrop-blur-md sticky top-0 z-20 flex items-center justify-between">
      {/* Title & context */}
      <div>
        <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          {title}
        </h1>
        <p className="text-xs text-slate-400">{subtitle}</p>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {/* Period Selector Pills */}
        <div className="flex items-center bg-[#161F30] p-1 rounded-lg border border-[#243045]">
          <Calendar className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1" />
          {periods.map((p) => {
            const active = period === p.id;
            return (
              <button
                key={p.id}
                onClick={() => onPeriodChange(p.id)}
                className={cn(
                  'px-2.5 py-1 text-xs font-medium rounded-md transition-all',
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

        {/* Quick Add Operation */}
        <button
          onClick={onOpenAddModal}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/25 text-xs font-semibold transition"
          title="Добавить финансовую операцию"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>+ Операция</span>
        </button>

        {/* Notification Bell */}
        <button
          onClick={onOpenNotifications}
          className="relative p-2 rounded-lg bg-[#161F30] border border-[#243045] text-slate-300 hover:text-white hover:border-slate-600 transition"
          title="Центр уведомлений"
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
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-slate-400 hover:text-amber-300 hover:border-amber-500/40 text-xs font-medium transition"
          title="Восстановить исходные демонстрационные данные"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Сброс демо</span>
        </button>
      </div>
    </header>
  );
};
