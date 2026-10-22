import React from 'react';
import {
  FileQuestion,
  Home,
  Layers,
  ArrowRight,
  Package,
  ShoppingCart,
  ArrowLeftRight,
  FileSpreadsheet,
  Settings,
} from 'lucide-react';

interface NotFoundPageProps {
  currentPath: string;
  onNavigate: (tab: string) => void;
  onReturnToCases: () => void;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({
  currentPath,
  onNavigate,
  onReturnToCases,
}) => {
  const quickLinks = [
    { id: 'dashboard', label: 'Сводный дашборд', icon: Home, desc: 'Финансовая аналитика и ключевые показатели' },
    { id: 'inventory', label: 'Склад и остатки', icon: Package, desc: 'Контроль остатков, списания и экспорт' },
    { id: 'orders', label: 'Заказы поставщикам', icon: ShoppingCart, desc: 'Оформление поставок и приемка' },
    { id: 'comparison', label: 'Сравнение цен', icon: ArrowLeftRight, desc: 'Калькулятор партий и поставщики' },
    { id: 'reports', label: 'Шаблоны отчетов', icon: FileSpreadsheet, desc: 'Конструктор и экспорт в Excel' },
    { id: 'settings', label: 'Настройки системы', icon: Settings, desc: 'Реквизиты, команда и журнал аудита' },
  ];

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto text-center">
      {/* 404 Glass Card */}
      <div className="w-full rounded-3xl bg-[#161F30] border border-[#243045] p-6 sm:p-10 shadow-2xl relative overflow-hidden space-y-6">
        {/* Decorative background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-32 bg-emerald-500/10 blur-3xl pointer-events-none rounded-full" />

        <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-[#243045] flex items-center justify-center mx-auto text-emerald-400 shadow-inner">
          <FileQuestion className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <div className="text-4xl sm:text-6xl font-extrabold tracking-tight font-mono bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
            404
          </div>
          <h2 className="text-lg sm:text-2xl font-bold text-white tracking-tight">
            Страница не найдена
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
            Запрошенный адрес{' '}
            <code className="px-2 py-0.5 rounded-lg bg-[#0B0F17] border border-[#243045] text-rose-300 font-mono text-xs">
              {currentPath || window.location.pathname}
            </code>{' '}
            не существует в системе BizMind или был перемещен.
          </p>
        </div>

        {/* Primary Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={() => onNavigate('dashboard')}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 transition shadow-lg shadow-emerald-500/20"
          >
            <Home className="w-4 h-4" />
            <span>На Главный дашборд</span>
          </button>
          <button
            onClick={onReturnToCases}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-[#0B0F17] hover:bg-[#1E293B] border border-[#243045] text-slate-300 font-semibold text-xs flex items-center justify-center gap-2 transition"
          >
            <Layers className="w-4 h-4 text-emerald-400" />
            <span>К выбору демо-кейса</span>
          </button>
        </div>

        {/* Quick Links Grid */}
        <div className="pt-6 border-t border-[#243045]">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 text-left">
            Популярные разделы системы:
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-left">
            {quickLinks.map((link) => {
              const Icon = link.icon;
              return (
                <button
                  key={link.id}
                  onClick={() => onNavigate(link.id)}
                  className="p-3 rounded-xl bg-[#0B0F17] hover:bg-slate-800/60 border border-[#243045] hover:border-emerald-500/40 transition group flex flex-col justify-between"
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-bold text-white group-hover:text-emerald-400 transition flex items-center gap-1.5">
                      <Icon className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      {link.label}
                    </span>
                    <ArrowRight className="w-3 h-3 text-slate-600 group-hover:text-emerald-400 transition" />
                  </div>
                  <p className="text-[10px] text-slate-400 line-clamp-2">
                    {link.desc}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
export default NotFoundPage;
