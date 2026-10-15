import React, { useEffect, useState } from 'react';
import {
  ArrowLeftRight,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Truck,
  Box,
  Calendar,
  Sparkles,
  Info,
  ShieldAlert,
} from 'lucide-react';
import { Product, PriceComparison } from '../types';
import { api } from '../services/api';
import { formatTenge, formatDate, formatPercent } from '../utils/formatters';

interface ComparisonPageProps {
  selectedProductId?: number | null;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({
  selectedProductId,
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [activeProductId, setActiveProductId] = useState<number>(
    selectedProductId || 0
  );
  const [quantity, setQuantity] = useState<number>(20);
  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch products list on mount / refresh
  useEffect(() => {
    api.getProducts().then((res) => {
      setProducts(res);
      if (res.length > 0) {
        if (!selectedProductId || !res.some((p) => p.id === selectedProductId)) {
          setActiveProductId(res[0].id);
        } else {
          setActiveProductId(selectedProductId);
        }
      }
    });
  }, [selectedProductId]);

  // Fetch comparison data whenever product or quantity changes
  useEffect(() => {
    if (!activeProductId) return;
    setLoading(true);
    api.comparePrices(activeProductId, quantity)
      .then((res) => setComparison(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [activeProductId, quantity]);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            Сравнение предложений поставщиков
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Анализ альтернативных прайс-листов на основе сопоставимых единиц измерения
          </p>
        </div>

        {/* Product Dropdown Selector */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
          <label className="text-xs text-slate-400">Выберите товар:</label>
          <select
            value={activeProductId}
            onChange={(e) => setActiveProductId(Number(e.target.value))}
            className="w-full sm:w-auto px-4 py-2.5 sm:py-2 rounded-xl bg-[#161F30] border border-[#243045] text-white text-xs font-semibold focus:outline-none focus:border-emerald-500 shadow-md"
          >
            {products.map((p) => (
              <option key={p.id} value={p.id} className="bg-[#0F172A]">
                {p.name} ({p.category})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="p-20 text-center text-slate-400 text-xs">
          Загрузка и пересчет предложений...
        </div>
      ) : comparison ? (
        <div className="space-y-6">
          {/* Current Supplier & Price Jump Card */}
          <div className="p-4 sm:p-6 rounded-2xl bg-[#161F30] border border-[#243045] relative overflow-hidden">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div>
                <div className="flex flex-wrap items-center gap-2 mb-1.5">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Текущее состояние закупки
                  </span>
                  {comparison.price_change_percent && comparison.price_change_percent > 0 && (
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1">
                      <TrendingUp className="w-3.5 h-3.5" />
                      Повышение цены {formatPercent(comparison.price_change_percent)}
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-bold text-white">
                  {comparison.product_name}
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Текущий поставщик: <strong className="text-slate-200">{comparison.current_supplier_name || 'Не указан'}</strong>
                </p>
              </div>

              {/* Price Stats */}
              <div className="grid grid-cols-2 sm:flex sm:items-center gap-4 sm:gap-6 bg-[#0B0F17] p-3.5 sm:p-4 rounded-xl border border-[#243045] w-full lg:w-auto">
                <div>
                  <div className="text-[11px] text-slate-400">Предыдущая цена</div>
                  <div className="text-sm font-semibold font-mono text-slate-400 mt-0.5">
                    {comparison.previous_unit_price ? formatTenge(comparison.previous_unit_price) : '—'}
                  </div>
                </div>

                <div className="hidden sm:block w-px h-8 bg-[#243045]"></div>

                <div>
                  <div className="text-[11px] text-slate-400">Новая цена закупки</div>
                  <div className="text-xl font-bold font-mono text-rose-400 mt-0.5">
                    {formatTenge(comparison.current_unit_price)}
                  </div>
                  <div className="text-[10px] text-slate-500">за 1 {comparison.unit}</div>
                </div>
              </div>
            </div>

            {/* Interactive Quantity Form */}
            <div className="mt-6 pt-5 border-t border-[#243045] flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
                <label className="text-xs font-semibold text-slate-300">
                  Планируемый объем партии ({comparison.unit}):
                </label>
                <div className="flex flex-wrap items-center gap-2">
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, Number(e.target.value)))}
                    className="w-24 px-3 py-1.5 rounded-lg bg-[#0B0F17] border border-[#243045] font-mono text-sm font-bold text-white text-center focus:outline-none focus:border-emerald-500"
                  />
                  <div className="flex flex-wrap gap-1.5">
                    {[10, 20, 50, 100].map((val) => (
                      <button
                        key={val}
                        onClick={() => setQuantity(val)}
                        className={`px-2.5 py-1 rounded-md text-xs font-medium transition ${
                          quantity === val
                            ? 'bg-emerald-500 text-slate-950 font-bold'
                            : 'bg-[#0B0F17] border border-[#243045] text-slate-400 hover:text-white'
                        }`}
                      >
                        {val} {comparison.unit}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {comparison.best_offer && (
                <div className="text-left lg:text-right bg-slate-950/40 p-3 rounded-xl border border-slate-800/80 lg:border-none lg:bg-transparent lg:p-0">
                  <div className="text-[11px] text-slate-400">
                    Максимальная потенциальная разница на объем {quantity} {comparison.unit}:
                  </div>
                  <div className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
                    {formatTenge(comparison.best_offer.total_difference)}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Formula and Methodology Disclaimer */}
          <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex items-start gap-3 text-xs text-slate-400 leading-relaxed">
            <Info className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-300">Методика сопоставления: </strong>
              {comparison.formula_note}
              <div className="mt-1 text-[11px] text-slate-500">
                Оценка носит демонстрационный характер. Окончательное решение о смене поставщика требует согласования условий оплаты и стабильности поставок.
              </div>
            </div>
          </div>

          {/* Alternative Offers List / Cards */}
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-3">
              <h3 className="text-sm font-bold text-white">
                Доступные предложения поставщиков ({comparison.alternative_offers.length})
              </h3>
              <span className="text-xs text-slate-400">
                Сортировка: от наиболее выгодной цены за единицу
              </span>
            </div>

            {comparison.alternative_offers.length === 0 ? (
              <div className="p-12 rounded-2xl bg-[#161F30] border border-[#243045] text-center text-slate-400 text-xs">
                По данному товару пока нет загруженных альтернативных предложений в каталоге.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {comparison.alternative_offers.map((offer) => {
                  const isCurrent =
                    offer.supplier_id === comparison.current_supplier_id;
                  const isBest =
                    comparison.best_offer?.supplier_id === offer.supplier_id;

                  return (
                    <div
                      key={offer.supplier_id}
                      className={`p-5 rounded-2xl flex flex-col justify-between transition border relative ${
                        isBest
                          ? 'bg-gradient-to-b from-[#162725] to-[#161F30] border-emerald-500/50 shadow-lg shadow-emerald-500/10'
                          : isCurrent
                          ? 'bg-[#161F30] border-rose-500/30'
                          : 'bg-[#161F30] border-[#243045] hover:border-slate-600'
                      }`}
                    >
                      {/* Badge */}
                      <div className="flex items-center justify-between mb-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                            isBest
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : isCurrent
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                              : 'bg-slate-800 text-slate-400 border border-slate-700'
                          }`}
                        >
                          {isBest
                            ? '★ Рекомендуемая альтернатива'
                            : isCurrent
                            ? 'Текущий поставщик'
                            : 'Альтернатива'}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {offer.is_demo ? 'Демо-каталог' : 'Импортирован'}
                        </span>
                      </div>

                      {/* Supplier & Price */}
                      <div>
                        <h4 className="text-base font-bold text-white">
                          {offer.supplier_name}
                        </h4>

                        <div className="mt-3 flex items-baseline gap-2">
                          <span className="text-2xl font-bold font-mono text-white">
                            {formatTenge(offer.offered_price)}
                          </span>
                          <span className="text-xs text-slate-400">
                            / 1 {offer.unit}
                          </span>
                        </div>

                        {/* Difference per unit */}
                        <div className="mt-2 text-xs">
                          {offer.unit_difference > 0 ? (
                            <span className="text-emerald-400 font-semibold">
                              Выгоднее на {formatTenge(offer.unit_difference)} / {offer.unit}
                            </span>
                          ) : offer.unit_difference < 0 ? (
                            <span className="text-rose-400 font-semibold">
                              Дороже на {formatTenge(Math.abs(offer.unit_difference))} / {offer.unit}
                            </span>
                          ) : (
                            <span className="text-slate-400">
                              Цена равна текущей
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Conditions list */}
                      <div className="mt-4 pt-4 border-t border-[#243045] space-y-2 text-xs text-slate-300">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 flex items-center gap-1.5">
                            <Box className="w-3.5 h-3.5" /> Мин. партия:
                          </span>
                          <span className="font-mono font-medium">
                            {offer.minimum_order_quantity} {offer.unit}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 flex items-center gap-1.5">
                            <Truck className="w-3.5 h-3.5" /> Доставка:
                          </span>
                          <span className="font-mono font-medium">
                            {offer.delivery_cost === 0
                              ? 'Бесплатно'
                              : formatTenge(offer.delivery_cost)}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5" /> Обновлено:
                          </span>
                          <span className="text-[11px] text-slate-400">
                            {formatDate(offer.updated_at)}
                          </span>
                        </div>
                      </div>

                      {/* Total calculated difference box */}
                      <div className="mt-4 p-3 rounded-xl bg-[#0B0F17] border border-[#243045] text-xs">
                        <div className="text-[11px] text-slate-400">
                          Итого на партию ({quantity} {offer.unit}):
                        </div>
                        <div className="flex items-baseline justify-between mt-1">
                          <span className="font-mono text-white">
                            {formatTenge(offer.offered_price * quantity)}
                          </span>
                          <span
                            className={`font-mono font-bold ${
                              offer.total_difference > 0
                                ? 'text-emerald-400'
                                : 'text-slate-400'
                            }`}
                          >
                            {offer.total_difference > 0
                              ? `−${formatTenge(offer.total_difference)}`
                              : '0 ₸'}
                          </span>
                        </div>
                        {offer.delivery_cost > 0 && (
                          <div className="text-[10px] text-slate-500 mt-1">
                            С учетом доставки: {formatTenge(offer.total_difference_with_delivery)} разница
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
