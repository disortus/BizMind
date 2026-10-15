import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  AlertTriangle,
  ArrowRight,
  ShoppingBag,
  Sparkles,
  Layers,
  ChevronRight,
  PieChart as PieIcon,
  Calculator,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { DashboardSummary } from '../types';
import { api } from '../services/api';
import { formatTenge, formatPercent, formatDate } from '../utils/formatters';
import { PriceAlertBanner } from '../components/PriceAlertBanner';

interface DashboardPageProps {
  period: string;
  onNavigate: (tab: string, productId?: number) => void;
}

const CATEGORY_COLORS = [
  '#10B981', // Emerald
  '#06B6D4', // Cyan
  '#F59E0B', // Amber
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#3B82F6', // Blue
  '#64748B', // Slate
];

export const DashboardPage: React.FC<DashboardPageProps> = ({ period, onNavigate }) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [interactiveQty, setInteractiveQty] = useState(20);

  useEffect(() => {
    setLoading(true);
    api.getDashboard(period)
      .then((res) => {
        setData(res);
        const feat = res.featured_comparison;
        if (feat) {
          setInteractiveQty(feat.selected_quantity || (feat.unit === 'упак' ? 50 : 20));
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [period]);

  const featuredComp = data?.featured_comparison;
  const isPackaging = featuredComp?.unit === 'упак';

  // Sync default quantity when featuredComp changes (e.g. on org switch)
  useEffect(() => {
    if (featuredComp) {
      setInteractiveQty(featuredComp.selected_quantity || (featuredComp.unit === 'упак' ? 50 : 20));
    }
  }, [featuredComp?.product_id, featuredComp?.unit]);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Загрузка аналитических данных...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-slate-400">
        Не удалось загрузить данные дашборда.
      </div>
    );
  }

  const currentPrice = featuredComp?.current_unit_price || 0;
  const altPrice = featuredComp?.best_offer?.offered_price || 0;
  const unitDiff = Math.max(0, currentPrice - altPrice);
  const calculatedSavings = unitDiff * interactiveQty;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* 1. Price Spike Highlight Banner */}
      <PriceAlertBanner
        featuredComp={featuredComp}
        onGoToComparison={(pid) => onNavigate('comparison', pid || featuredComp?.product_id)}
      />

      {/* 2. Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Expenses */}
        <div className="p-5 rounded-2xl bg-[#161F30] border border-[#243045] relative overflow-hidden group hover:border-[#334155] transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Расходы за период</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white font-mono tracking-tight">
            {formatTenge(data.total_expenses)}
          </div>
          <div className="mt-2 flex items-center gap-2 text-xs">
            <span
              className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded font-semibold text-[11px] ${
                data.expenses_change_percent > 0
                  ? 'bg-rose-500/15 text-rose-300'
                  : 'bg-emerald-500/15 text-emerald-300'
              }`}
            >
              {data.expenses_change_percent > 0 ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              {formatPercent(data.expenses_change_percent)}
            </span>
            <span className="text-slate-400 text-[11px]">к пред. периоду</span>
          </div>
        </div>

        {/* Potential Savings */}
        <div className="p-5 rounded-2xl bg-gradient-to-br from-[#161F30] to-[#12232E] border border-emerald-500/30 relative overflow-hidden group hover:border-emerald-500/50 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span className="text-emerald-300 font-medium">Потенциал оптимизации</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-300">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-300 font-mono tracking-tight">
            {formatTenge(data.potential_savings_monthly)}
          </div>
          <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between">
            <span>в месяц при смене поставщиков</span>
            <button
              onClick={() => onNavigate('comparison')}
              className="text-emerald-400 hover:text-emerald-300 font-semibold inline-flex items-center gap-0.5"
            >
              Детали <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Total Income */}
        <div className="p-5 rounded-2xl bg-[#161F30] border border-[#243045] relative overflow-hidden group hover:border-[#334155] transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Выручка кофейни</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white font-mono tracking-tight">
            {formatTenge(data.total_income)}
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Касса и эквайринг за период
          </div>
        </div>

        {/* Active Suppliers & Alerts */}
        <div className="p-5 rounded-2xl bg-[#161F30] border border-[#243045] relative overflow-hidden group hover:border-[#334155] transition">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>Поставщики и события</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">
              {data.active_suppliers_count}
            </span>
            <span className="text-xs text-slate-400">активных поставщиков</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/20">
              {data.pending_alerts_count} сигнала
            </span>
            <button
              onClick={() => onNavigate('notifications')}
              className="text-slate-400 hover:text-white text-[11px] transition"
            >
              Смотреть все →
            </button>
          </div>
        </div>
      </div>

      {/* 3. Charts Row: Dynamic Expense Timeline & Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white">Динамика расходов и выручки</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Фактические платежи и поступления Cafe Aroma за выбранный период
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                  <span className="text-slate-300">Расходы</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                  <span className="text-slate-300">Выручка</span>
                </div>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.dynamics}>
                  <defs>
                    <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                  <XAxis
                    dataKey="date"
                    stroke="#64748B"
                    fontSize={11}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="#64748B"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                  />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="p-3 rounded-xl bg-[#0F172A] border border-[#334155] shadow-xl text-xs space-y-1">
                            <div className="font-bold text-white">{label}</div>
                            {payload.map((entry: any, idx: number) => (
                              <div
                                key={idx}
                                className="flex items-center justify-between gap-3 text-slate-300"
                              >
                                <span style={{ color: entry.color }}>
                                  {entry.name === 'amount' ? 'Расходы:' : 'Выручка:'}
                                </span>
                                <span className="font-mono font-bold text-white">
                                  {formatTenge(entry.value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="amount"
                    name="amount"
                    stroke="#10B981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#expenseGrad)"
                  />
                  <Area
                    type="monotone"
                    dataKey="income"
                    name="income"
                    stroke="#06B6D4"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#incomeGrad)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#243045] flex items-center justify-between text-xs text-slate-400">
            <span>Данные синхронизированы из SQLite базы</span>
            <button
              onClick={() => onNavigate('finances')}
              className="text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
            >
              Все операции ({data.dynamics.length}) →
            </button>
          </div>
        </div>

        {/* Category Breakdown (1 col) */}
        <div className="p-6 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold text-white">Структура расходов</h3>
              <PieIcon className="w-4 h-4 text-slate-400" />
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Распределение бюджета по ключевым категориям
            </p>

            {/* Donut chart */}
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.categories}
                    dataKey="amount"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={65}
                    paddingAngle={3}
                  >
                    {data.categories.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const item = payload[0].payload;
                        return (
                          <div className="p-2.5 rounded-lg bg-[#0F172A] border border-[#334155] shadow-xl text-xs space-y-0.5">
                            <div className="font-semibold text-white">{item.category}</div>
                            <div className="font-mono text-emerald-400 font-bold">
                              {formatTenge(item.amount)} ({item.percentage}%)
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Categories list */}
            <div className="mt-3 space-y-2 max-h-48 overflow-y-auto pr-1">
              {data.categories.slice(0, 5).map((cat, idx) => (
                <div key={cat.category} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 min-w-0">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: CATEGORY_COLORS[idx % CATEGORY_COLORS.length] }}
                    ></span>
                    <span className="text-slate-300 truncate">{cat.category}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 font-mono">
                    <span className="text-white font-semibold">{formatTenge(cat.amount)}</span>
                    <span className="text-slate-500 text-[10px] w-9 text-right">
                      {cat.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#243045] text-center">
            <button
              onClick={() => onNavigate('finances')}
              className="text-xs text-slate-400 hover:text-white transition"
            >
              Подробный финансовый отчет →
            </button>
          </div>
        </div>
      </div>

      {/* 4. Interactive Supplier Comparison Mini-Tool */}
      {featuredComp && featuredComp.best_offer && (
        <div className="p-6 rounded-2xl bg-[#161F30] border border-[#243045] relative overflow-hidden">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-500/15 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                  <Calculator className="w-3 h-3" />
                  Экспресс-калькулятор закупки
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  {featuredComp.product_name}
                </span>
              </div>
              <h3 className="text-base font-bold text-white">
                Расчет потенциальной разницы при смене поставщика
              </h3>
              <p className="text-xs text-slate-400 mt-1 max-w-xl">
                Текущий поставщик <strong className="text-slate-200">{featuredComp.current_supplier_name}</strong> ({formatTenge(featuredComp.current_unit_price)}/{featuredComp.unit}) 
                против альтернативы <strong className="text-emerald-400">{featuredComp.best_offer.supplier_name}</strong> ({formatTenge(featuredComp.best_offer.offered_price)}/{featuredComp.unit}).
              </p>
            </div>

            {/* Slider and live result */}
            <div className="flex flex-col sm:flex-row items-center gap-6 bg-[#0B0F17] p-4 rounded-xl border border-[#243045] shrink-0">
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Объем закупки:</span>
                  <span className="font-mono text-emerald-400 font-bold">
                    {interactiveQty} {featuredComp.unit}
                  </span>
                </div>
                <input
                  type="range"
                  min={isPackaging ? 10 : 5}
                  max={isPackaging ? 200 : 100}
                  step={isPackaging ? 10 : 5}
                  value={interactiveQty}
                  onChange={(e) => setInteractiveQty(Number(e.target.value))}
                  className="w-48 accent-emerald-500 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span>{isPackaging ? '10 упак' : '5 кг'}</span>
                  <span>{isPackaging ? '100 упак' : '50 кг'}</span>
                  <span>{isPackaging ? '200 упак' : '100 кг'}</span>
                </div>
              </div>

              <div className="border-l border-[#243045] pl-6 text-left">
                <div className="text-[11px] text-slate-400">Потенциальная разница:</div>
                <div className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
                  {formatTenge(calculatedSavings)}
                </div>
                <div className="text-[10px] text-slate-500">
                  ({formatTenge(unitDiff)} на 1 {featuredComp.unit})
                </div>
              </div>

              <button
                onClick={() => onNavigate('comparison', featuredComp.product_id)}
                className="px-3.5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1 shadow-md transition"
              >
                <span>Сравнить</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. Bottom Row: Recent Purchases & System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Purchases (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#161F30] border border-[#243045]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Последние закупки кофейни</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Зафиксированные партии товаров и сырья
              </p>
            </div>
            <button
              onClick={() => onNavigate('purchases')}
              className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold"
            >
              Вся история закупок →
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase tracking-wider">
                  <th className="pb-2.5 font-medium">Товар</th>
                  <th className="pb-2.5 font-medium">Поставщик</th>
                  <th className="pb-2.5 font-medium">Дата</th>
                  <th className="pb-2.5 font-medium text-right">Объем</th>
                  <th className="pb-2.5 font-medium text-right">Цена за ед.</th>
                  <th className="pb-2.5 font-medium text-right">Итого</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243045]/60 text-slate-200">
                {data.recent_purchases.map((p) => (
                  <tr
                    key={p.id}
                    onClick={() => onNavigate('purchases', p.product_id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition"
                  >
                    <td className="py-2.5 font-medium text-white max-w-[200px] truncate">
                      {p.product_name}
                    </td>
                    <td className="py-2.5 text-slate-400">{p.supplier_name}</td>
                    <td className="py-2.5 text-slate-400 whitespace-nowrap">
                      {formatDate(p.purchase_date)}
                    </td>
                    <td className="py-2.5 text-right font-mono">
                      {p.quantity} {p.unit}
                    </td>
                    <td className="py-2.5 text-right font-mono font-semibold">
                      {formatTenge(p.unit_price)}
                    </td>
                    <td className="py-2.5 text-right font-mono text-emerald-400 font-bold">
                      {formatTenge(p.total_price)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Demo Shortcuts & Actions (1 col) */}
        <div className="p-6 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col justify-between space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white mb-1">Сценарии демонстрации</h3>
            <p className="text-xs text-slate-400 mb-4">
              Ключевые точки пользовательского пути жюри
            </p>

            <div className="space-y-2.5">
              <button
                onClick={() => onNavigate('import')}
                className="w-full p-3 rounded-xl bg-[#0B0F17] hover:bg-slate-800/60 border border-[#243045] text-left transition flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-white group-hover:text-emerald-400 transition">
                    1. Загрузка старого Excel
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Импорт legacy_finances.xlsx
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition" />
              </button>

              <button
                onClick={() => onNavigate('comparison', 1)}
                className="w-full p-3 rounded-xl bg-[#0B0F17] hover:bg-slate-800/60 border border-[#243045] text-left transition flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-white group-hover:text-emerald-400 transition">
                    2. Сравнение поставщиков кофе
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Aroma Direct vs Coffee Roasters (+15%)
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition" />
              </button>

              <button
                onClick={() => onNavigate('forecast')}
                className="w-full p-3 rounded-xl bg-[#0B0F17] hover:bg-slate-800/60 border border-[#243045] text-left transition flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-white group-hover:text-emerald-400 transition">
                    3. Прогноз потребности в молоке
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Остаток 12л при минимуме 25л
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition" />
              </button>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 text-center">
            Все расчеты произведены на основе бизнес-логики и SQL-агрегатов без сторонних API.
          </div>
        </div>
      </div>
    </div>
  );
};
