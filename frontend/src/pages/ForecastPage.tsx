import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  PackageCheck,
  ArrowRight,
  Info,
  Clock,
  ShieldAlert,
} from 'lucide-react';
import { ForecastSummary } from '../types';
import { api } from '../services/api';
import { formatTenge } from '../utils/formatters';

interface ForecastPageProps {
  onGoToComparison: (productId: number) => void;
}

export const ForecastPage: React.FC<ForecastPageProps> = ({ onGoToComparison }) => {
  const [data, setData] = useState<ForecastSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'critical' | 'low'>('all');

  useEffect(() => {
    setLoading(true);
    api.getForecast()
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-16 text-center text-slate-500 text-xs">
        Расчет статистических прогнозов потребности...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-slate-400">
        Не удалось загрузить прогноз остатков.
      </div>
    );
  }

  const filteredItems = data.items.filter((item) => {
    if (filter === 'critical') return item.status === 'critical';
    if (filter === 'low') return item.status === 'low' || item.status === 'critical';
    return true;
  });

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Позиций на мониторинге</div>
          <div className="text-xl font-bold font-mono text-white">
            {data.total_products_tracked} товаров
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Кофе, молоко, сиропы, упаковка
          </div>
        </div>

        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30">
          <div className="text-xs text-rose-300 mb-1 flex items-center justify-between">
            <span>Критический остаток</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-xl font-bold font-mono text-rose-300">
            {data.critical_items_count} позиции
          </div>
          <div className="text-[11px] text-rose-400/80 mt-1">
            Хватит менее чем на 3 дня (молоко, крышки)
          </div>
        </div>

        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30">
          <div className="text-xs text-amber-300 mb-1 flex items-center justify-between">
            <span>Заканчиваются в течение недели</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold font-mono text-amber-300">
            {data.low_stock_items_count} позиций
          </div>
          <div className="text-[11px] text-amber-400/80 mt-1">
            Рекомендуется включить в ближайший заказ
          </div>
        </div>
      </div>

      {/* Info notice */}
      <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex items-start gap-3 text-xs text-slate-400">
        <Info className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-300">Методика прогнозирования: </strong>
          Оценка рассчитана на основе фактической истории закупок, среднего ежедневного расхода и доступных данных об остатках на складе кофейни Cafe Aroma.
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 p-1 rounded-xl bg-[#161F30] border border-[#243045] text-xs">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg transition ${
              filter === 'all'
                ? 'bg-slate-700 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Все товары ({data.items.length})
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-3 py-1.5 rounded-lg transition ${
              filter === 'critical'
                ? 'bg-rose-500/20 text-rose-300 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Критический остаток ({data.critical_items_count})
          </button>
        </div>

        <span className="text-xs text-slate-500">
          Показано: {filteredItems.length} из {data.items.length}
        </span>
      </div>

      {/* Forecast Table */}
      <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase tracking-wider bg-[#0F172A]/50">
                <th className="py-3 px-4 font-medium">Товар</th>
                <th className="py-3 px-4 font-medium">Категория</th>
                <th className="py-3 px-4 font-medium text-right">Остаток / Мин.</th>
                <th className="py-3 px-4 font-medium text-right">Расход в день</th>
                <th className="py-3 px-4 font-medium text-center">Запас на (дней)</th>
                <th className="py-3 px-4 font-medium text-right">Потребность 14д</th>
                <th className="py-3 px-4 font-medium text-right">Рекомендуемый заказ</th>
                <th className="py-3 px-4 font-medium text-center">Статус</th>
                <th className="py-3 px-4 font-medium text-center">Действие</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#243045]/60 text-slate-300">
              {filteredItems.map((item) => {
                const isCritical = item.status === 'critical';
                const isLow = item.status === 'low';

                return (
                  <tr
                    key={item.product_id}
                    className={`hover:bg-slate-800/30 transition ${
                      isCritical ? 'bg-rose-950/15' : isLow ? 'bg-amber-950/10' : ''
                    }`}
                  >
                    <td className="py-3 px-4 font-semibold text-white">
                      <div>{item.product_name}</div>
                      <div className="text-[10px] text-slate-500">{item.note}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{item.category}</td>
                    <td className="py-3 px-4 text-right font-mono">
                      <span className={isCritical ? 'text-rose-400 font-bold' : 'text-white'}>
                        {item.current_stock}
                      </span>{' '}
                      / {item.minimum_stock} {item.unit}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-300">
                      ~{item.avg_daily_consumption} {item.unit}/дн.
                    </td>
                    <td className="py-3 px-4 text-center font-mono font-bold">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[11px] ${
                          isCritical
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : isLow
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-emerald-500/10 text-emerald-300'
                        }`}
                      >
                        {item.days_left !== null ? `${item.days_left} дн.` : '—'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-300">
                      {item.forecast_14d} {item.unit}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-emerald-400">
                      {item.recommended_order_quantity > 0
                        ? `${item.recommended_order_quantity} ${item.unit}`
                        : 'Не требуется'}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          isCritical
                            ? 'bg-rose-500/20 text-rose-300'
                            : isLow
                            ? 'bg-amber-500/20 text-amber-300'
                            : 'bg-emerald-500/20 text-emerald-300'
                        }`}
                      >
                        {isCritical
                          ? 'Критический'
                          : isLow
                          ? 'Заканчивается'
                          : 'В норме'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => onGoToComparison(item.product_id)}
                        className="px-2.5 py-1 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-400 text-[11px] font-medium transition inline-flex items-center gap-1"
                      >
                        <span>Сравнить</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
