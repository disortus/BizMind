import React, { useEffect, useState } from 'react';
import { X, ArrowRight, TrendingUp, TrendingDown, Clock, ShieldCheck } from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { ProductPriceHistory } from '../types';
import { api } from '../services/api';
import { formatTenge, formatDate, formatPercent } from '../utils/formatters';

interface ProductHistoryModalProps {
  productId: number | null;
  onClose: () => void;
  onGoToComparison: (productId: number) => void;
}

export const ProductHistoryModal: React.FC<ProductHistoryModalProps> = ({
  productId,
  onClose,
  onGoToComparison,
}) => {
  const [data, setData] = useState<ProductPriceHistory | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    api.getProductHistory(productId)
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [productId]);

  if (!productId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-[#161F30] border border-[#243045] rounded-2xl shadow-2xl p-4 sm:p-6 overflow-hidden max-h-[92dvh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#243045]">
          <div>
            <h3 className="text-base font-bold text-white">
              {loading ? 'Загрузка...' : data?.product_name || 'История закупочных цен'}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Динамика стоимости закупки за сопоставимую единицу ({data?.unit || 'ед.'})
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="py-20 text-center text-slate-500 text-xs">Загрузка истории цен...</div>
        ) : data ? (
          <div className="mt-4 space-y-5 sm:space-y-6 overflow-y-auto pr-1">
            {/* Price Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3">
              <div className="p-3.5 rounded-xl bg-[#0B0F17] border border-[#243045]">
                <div className="text-[11px] text-slate-400">Последняя цена</div>
                <div className="text-lg font-bold text-white font-mono mt-0.5">
                  {formatTenge(data.current_price)}
                </div>
                <div className="text-[10px] text-slate-500">за 1 {data.unit}</div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#0B0F17] border border-[#243045]">
                <div className="text-[11px] text-slate-400">Предыдущая цена</div>
                <div className="text-lg font-bold text-slate-300 font-mono mt-0.5">
                  {data.previous_price ? formatTenge(data.previous_price) : '—'}
                </div>
                <div className="text-[10px] text-slate-500">до изменения</div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#0B0F17] border border-[#243045]">
                <div className="text-[11px] text-slate-400">Изменение</div>
                <div
                  className={`text-lg font-bold font-mono mt-0.5 flex items-center gap-1 ${
                    (data.price_change_percent || 0) > 0
                      ? 'text-rose-400'
                      : (data.price_change_percent || 0) < 0
                      ? 'text-emerald-400'
                      : 'text-slate-300'
                  }`}
                >
                  {(data.price_change_percent || 0) > 0 && <TrendingUp className="w-4 h-4" />}
                  {(data.price_change_percent || 0) < 0 && <TrendingDown className="w-4 h-4" />}
                  {data.price_change_percent !== null && data.price_change_percent !== undefined
                    ? formatPercent(data.price_change_percent)
                    : '—'}
                </div>
                <div className="text-[10px] text-slate-500">к прошлой закупке</div>
              </div>
            </div>

            {/* Chart */}
            <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#243045]">
              <div className="text-xs font-semibold text-slate-300 mb-3 flex items-center justify-between">
                <span>График изменения закупочной цены</span>
                <span className="text-[11px] text-slate-500 font-normal">₸ / {data.unit}</span>
              </div>
              <div className="h-44 sm:h-52 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(val) => formatDate(val)}
                      stroke="#64748B"
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      stroke="#64748B"
                      fontSize={11}
                      tickLine={false}
                      domain={['auto', 'auto']}
                      tickFormatter={(val) => `${val / 1000}k`}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const p = payload[0].payload;
                          return (
                            <div className="p-2.5 rounded-lg bg-[#161F30] border border-[#334155] shadow-xl text-xs space-y-1">
                              <div className="font-semibold text-white">{formatDate(p.date)}</div>
                              <div className="text-emerald-400 font-mono font-bold">
                                {formatTenge(p.price)} / {data.unit}
                              </div>
                              <div className="text-slate-400 text-[11px]">Поставщик: {p.supplier_name}</div>
                              <div className="text-slate-400 text-[11px]">Партия: {p.quantity} {data.unit}</div>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="#10B981"
                      strokeWidth={3}
                      dot={{ fill: '#10B981', r: 5 }}
                      activeDot={{ r: 7, fill: '#34D399' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Action Bar */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/30 to-[#161F30] border border-emerald-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="text-xs font-bold text-white">Есть предложения других поставщиков?</div>
                <div className="text-[11px] text-slate-400">
                  Сравните условия, фасовку и рассчитайте выгоду на партию
                </div>
              </div>
              <button
                onClick={() => {
                  onClose();
                  onGoToComparison(data.product_id);
                }}
                className="w-full sm:w-auto justify-center px-4 py-2.5 sm:py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition"
              >
                <span>Сравнить поставщиков</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
