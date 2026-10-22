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
  ShieldCheck,
  Building2,
  Search,
  Filter,
  FileSpreadsheet,
  User,
  Phone,
  Mail,
  Award,
  RefreshCw,
  Clock,
  Layers,
} from 'lucide-react';
import { Product, PriceComparison, Supplier } from '../types';
import { api } from '../services/api';
import { formatTenge, formatDate, formatPercent } from '../utils/formatters';

interface ComparisonPageProps {
  selectedProductId?: number | null;
  initialQuantity?: number | null;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({
  selectedProductId,
  initialQuantity,
}) => {
  const [activeTab, setActiveTab] = useState<'compare' | 'catalog'>('compare');
  const [products, setProducts] = useState<Product[]>([]);
  const [activeProductId, setActiveProductId] = useState<number>(
    selectedProductId || 0
  );
  const [quantity, setQuantity] = useState<number>(
    initialQuantity && initialQuantity > 0 ? initialQuantity : 20
  );
  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [selectedOfferSupplierId, setSelectedOfferSupplierId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // Supplier Catalog state
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [supplierSearch, setSupplierSearch] = useState('');
  const [supplierSourceFilter, setSupplierSourceFilter] = useState<'all' | 'global' | 'imported' | 'manual'>('all');
  const [offerOriginFilter, setOfferOriginFilter] = useState<'all' | 'global' | 'imported'>('all');

  // Sync initialQuantity when it changes from outside (e.g. Dashboard slider)
  useEffect(() => {
    if (initialQuantity && initialQuantity > 0) {
      setQuantity(initialQuantity);
    }
  }, [initialQuantity]);

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
    if (!activeProductId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api.comparePrices(activeProductId, quantity)
      .then((res) => {
        setComparison(res);
        if (res.best_offer?.supplier_id) {
          setSelectedOfferSupplierId((prev) => {
            if (prev && res.alternative_offers.some((o) => o.supplier_id === prev)) {
              return prev;
            }
            return res.best_offer?.supplier_id || null;
          });
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [activeProductId, quantity]);

  // Fetch suppliers list for catalog tab
  const fetchSuppliers = () => {
    setCatalogLoading(true);
    api.getSuppliers()
      .then((res) => setSuppliers(res))
      .catch((err) => console.error(err))
      .finally(() => setCatalogLoading(false));
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  // Filter suppliers for catalog
  const filteredSuppliers = suppliers.filter((s) => {
    const isGlobal = s.is_global || s.source_type === 'global';
    if (supplierSourceFilter === 'global' && !isGlobal) return false;
    if (supplierSourceFilter === 'imported' && s.source_type !== 'imported') return false;
    if (supplierSourceFilter === 'manual' && s.source_type !== 'manual') return false;

    if (!supplierSearch.trim()) return true;
    const query = supplierSearch.toLowerCase();
    return (
      s.name.toLowerCase().includes(query) ||
      (s.contact_name && s.contact_name.toLowerCase().includes(query)) ||
      (s.phone && s.phone.toLowerCase().includes(query)) ||
      (s.email && s.email.toLowerCase().includes(query))
    );
  });

  const globalSuppliersCount = suppliers.filter((s) => s.is_global || s.source_type === 'global').length;
  const importedSuppliersCount = suppliers.filter((s) => s.source_type === 'imported').length;
  const manualSuppliersCount = suppliers.filter((s) => s.source_type === 'manual').length;

  // Filter alternative offers by origin
  const displayedOffers = (comparison?.alternative_offers || []).filter((offer) => {
    const isGlobal = offer.is_global_supplier || offer.supplier_source_type === 'global';
    if (offerOriginFilter === 'global' && !isGlobal) return false;
    if (offerOriginFilter === 'imported' && (isGlobal || offer.supplier_source_type === 'manual')) return false;
    return true;
  });

  // Selected offer for custom card calculation
  const selectedOffer =
    displayedOffers.find((o) => o.supplier_id === selectedOfferSupplierId) ||
    comparison?.alternative_offers.find((o) => o.supplier_id === selectedOfferSupplierId) ||
    comparison?.best_offer ||
    displayedOffers[0] ||
    null;

  const selectedUnitDiff = comparison && selectedOffer
    ? comparison.current_unit_price - selectedOffer.offered_price
    : 0;

  const selectedTotalDiff = selectedUnitDiff * quantity;
  const selectedDeliveryCost = selectedOffer?.delivery_cost || 0;
  const selectedTotalDiffWithDelivery = selectedTotalDiff - selectedDeliveryCost;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header & Tab Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <ArrowLeftRight className="w-5 h-5 text-emerald-400" />
            Поставщики и сравнение цен
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Анализ альтернативных предложений, сопоставление прайс-листов и каталог поставщиков
          </p>
        </div>

        {/* Tab switch pills */}
        <div className="flex items-center gap-1.5 p-1 bg-[#161F30] border border-[#243045] rounded-xl self-start md:self-auto">
          <button
            onClick={() => setActiveTab('compare')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
              activeTab === 'compare'
                ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ArrowLeftRight className="w-3.5 h-3.5" />
            Сравнение цен
          </button>
          <button
            onClick={() => setActiveTab('catalog')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
              activeTab === 'catalog'
                ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            Каталог поставщиков
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-800 text-slate-300 ml-0.5">
              {suppliers.length}
            </span>
          </button>
        </div>
      </div>

      {/* TAB 1: PRICE COMPARISON */}
      {activeTab === 'compare' && (
        <div className="space-y-6">
          {products.length === 0 ? (
            <div className="p-8 sm:p-12 rounded-2xl bg-[#161F30] border border-[#243045] text-center max-w-2xl mx-auto space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto text-indigo-400">
                <Building2 className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold text-white">
                Товары для сравнения цен пока не созданы
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                В этой организации ещё нет импортированных товаров. Вы можете ознакомиться с демонстрационным каталогом поставщиков BizMind прямо сейчас или загрузить начальные остатки через раздел импорта.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
                <button
                  onClick={() => setActiveTab('catalog')}
                  className="px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition flex items-center gap-1.5"
                >
                  <Building2 className="w-4 h-4" />
                  Открыть каталог поставщиков ({suppliers.length})
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Product Selector Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#161F30] border border-[#243045]">
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
                  <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-emerald-400" />
                    Товар для сравнения:
                  </label>
                  <select
                    value={activeProductId}
                    onChange={(e) => setActiveProductId(Number(e.target.value))}
                    className="w-full sm:w-auto px-4 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs font-semibold focus:outline-none focus:border-emerald-500 shadow-md"
                  >
                    {products.map((p) => (
                      <option key={p.id} value={p.id} className="bg-[#0F172A]">
                        {p.name} ({p.category})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Offer Origin Filter Toggle */}
                <div className="flex items-center gap-1.5 text-xs">
                  <span className="text-[11px] text-slate-400 mr-1 hidden sm:inline">Источник предложений:</span>
                  <button
                    onClick={() => setOfferOriginFilter('all')}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition ${
                      offerOriginFilter === 'all'
                        ? 'bg-[#243045] text-white border border-slate-600'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Все ({comparison?.alternative_offers.length || 0})
                  </button>
                  <button
                    onClick={() => setOfferOriginFilter('global')}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition ${
                      offerOriginFilter === 'global'
                        ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <Sparkles className="w-3 h-3 text-indigo-400" />
                    Из базы BizMind
                  </button>
                  <button
                    onClick={() => setOfferOriginFilter('imported')}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition ${
                      offerOriginFilter === 'imported'
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <FileSpreadsheet className="w-3 h-3 text-cyan-400" />
                    Импортированные
                  </button>
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

                      {/* Interactive Calculation Box for Selected Card */}
                      {selectedOffer ? (
                        <div className="text-left lg:text-right bg-[#0B0F17] p-3.5 sm:p-4 rounded-xl border border-emerald-500/30 w-full lg:w-auto shadow-md">
                          <div className="flex items-center justify-between lg:justify-end gap-2 mb-1">
                            <span className="text-[11px] text-slate-400">Расчет для карточки:</span>
                            <span className="font-bold text-xs text-emerald-300 flex items-center gap-1">
                              {selectedOffer.supplier_name}
                              {comparison.best_offer?.supplier_id === selectedOffer.supplier_id && (
                                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-500/30">
                                  ★ Топ
                                </span>
                              )}
                            </span>
                          </div>

                          <div className="text-xs text-slate-300">
                            Сумма партии ({quantity} {comparison.unit}):{' '}
                            <strong className="font-mono text-white">
                              {formatTenge(selectedOffer.offered_price * quantity)}
                            </strong>
                          </div>

                          <div className="mt-1 flex items-baseline justify-between lg:justify-end gap-2">
                            <span className="text-[11px] text-slate-400">
                              {selectedTotalDiff >= 0 ? 'Потенциальная экономия:' : 'Переплата к текущему:'}
                            </span>
                            <span
                              className={`text-xl font-bold font-mono ${
                                selectedTotalDiff >= 0 ? 'text-emerald-400' : 'text-rose-400'
                              }`}
                            >
                              {selectedTotalDiff >= 0
                                ? `+${formatTenge(selectedTotalDiff)}`
                                : `−${formatTenge(Math.abs(selectedTotalDiff))}`}
                            </span>
                          </div>

                          {selectedOffer.delivery_cost > 0 && (
                            <div className="text-[10px] text-slate-400 mt-0.5">
                              С учетом доставки ({formatTenge(selectedOffer.delivery_cost)}):{' '}
                              <span className={selectedTotalDiffWithDelivery >= 0 ? 'text-emerald-400 font-mono' : 'text-rose-400 font-mono'}>
                                {selectedTotalDiffWithDelivery >= 0
                                  ? `+${formatTenge(selectedTotalDiffWithDelivery)}`
                                  : `−${formatTenge(Math.abs(selectedTotalDiffWithDelivery))}`}
                              </span>
                            </div>
                          )}

                          <div className="text-[10px] text-slate-500 mt-1 italic">
                            Нажмите на любую карточку поставщика ниже для пересчета
                          </div>
                        </div>
                      ) : comparison.best_offer ? (
                        <div className="text-left lg:text-right bg-slate-950/40 p-3 rounded-xl border border-slate-800/80 lg:border-none lg:bg-transparent lg:p-0">
                          <div className="text-[11px] text-slate-400">
                            Максимальная потенциальная разница на объем {quantity} {comparison.unit}:
                          </div>
                          <div className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
                            {formatTenge(comparison.best_offer.total_difference)}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  </div>

                  {/* Formula and Methodology Disclaimer */}
                  <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex items-start gap-3 text-xs text-slate-400 leading-relaxed">
                    <Info className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-slate-300">Методика сопоставления: </strong>
                      {comparison.formula_note}
                      <div className="mt-1 text-[11px] text-slate-500">
                        Оценка потенциальной экономии рассчитывается для планового объема. Реализованная экономия подтверждается только после совершения фактической закупки.
                      </div>
                    </div>
                  </div>

                  {/* Alternative Offers List / Cards */}
                  <div>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-3">
                      <h3 className="text-sm font-bold text-white">
                        Доступные предложения ({displayedOffers.length} из {comparison.alternative_offers.length})
                      </h3>
                      <span className="text-xs text-slate-400">
                        Сортировка: от наиболее выгодной цены за единицу
                      </span>
                    </div>

                    {displayedOffers.length === 0 ? (
                      <div className="p-12 rounded-2xl bg-[#161F30] border border-[#243045] text-center text-slate-400 text-xs">
                        По выбранным критериям предложений не найдено. Попробуйте сбросить фильтр источника.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {displayedOffers.map((offer) => {
                          const isCurrent = offer.supplier_id === comparison.current_supplier_id;
                          const isBest = comparison.best_offer?.supplier_id === offer.supplier_id;
                          const isSelected = selectedOffer?.supplier_id === offer.supplier_id;
                          const isGlobalSupplier = offer.is_global_supplier || offer.supplier_source_type === 'global';
                          const cardDiff = (comparison.current_unit_price - offer.offered_price) * quantity;

                          return (
                            <div
                              key={offer.supplier_id}
                              onClick={() => setSelectedOfferSupplierId(offer.supplier_id)}
                              className={`p-5 rounded-2xl flex flex-col justify-between transition-all cursor-pointer relative border ${
                                isSelected
                                  ? 'bg-gradient-to-b from-[#182e27] to-[#161F30] border-emerald-400 ring-2 ring-emerald-500/50 shadow-xl shadow-emerald-500/15'
                                  : isBest
                                  ? 'bg-gradient-to-b from-[#162725] to-[#161F30] border-emerald-500/50 hover:border-emerald-400 shadow-lg shadow-emerald-500/10'
                                  : isCurrent
                                  ? 'bg-[#161F30] border-rose-500/30 hover:border-rose-400/50'
                                  : 'bg-[#161F30] border-[#243045] hover:border-slate-500'
                              }`}
                            >
                              {/* Top Badges: Status + Origin */}
                              <div>
                                <div className="flex flex-wrap items-center justify-between gap-1.5 mb-2.5">
                                  <div className="flex flex-wrap items-center gap-1.5">
                                    {isSelected && (
                                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500 text-slate-950 flex items-center gap-1 shadow-sm">
                                        <CheckCircle className="w-3 h-3" /> Выбрано
                                      </span>
                                    )}
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
                                        ? '★ Рекомендуемая'
                                        : isCurrent
                                        ? 'Текущий'
                                        : 'Альтернатива'}
                                    </span>
                                  </div>

                                  {/* Origin of Supplier Badge */}
                                  {isGlobalSupplier ? (
                                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1">
                                      <Sparkles className="w-3 h-3 text-indigo-400" />
                                      Из базы BizMind
                                    </span>
                                  ) : offer.supplier_source_type === 'imported' ? (
                                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                                      <FileSpreadsheet className="w-3 h-3 text-cyan-400" />
                                      Импортирован
                                    </span>
                                  ) : (
                                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                                      <User className="w-3 h-3 text-amber-400" />
                                      Вручную
                                    </span>
                                  )}
                                </div>

                                {/* Price Source Sub-badge */}
                                <div className="mb-3 flex items-center gap-1.5">
                                  <span className="text-[10px] text-slate-500">
                                    {offer.price_source === 'global_catalog'
                                      ? 'Прайс: Из каталога BizMind'
                                      : offer.price_source === 'imported'
                                      ? 'Прайс: Загружен пользователем'
                                      : 'Прайс: Ручной ввод'}
                                  </span>
                                </div>

                                {/* Supplier Name & Price */}
                                <h4 className="text-base font-bold text-white flex items-center justify-between gap-2">
                                  <span>{offer.supplier_name}</span>
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
                              <div>
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
                                <div className={`mt-4 p-3 rounded-xl border text-xs transition ${
                                  isSelected
                                    ? 'bg-[#0B0F17] border-emerald-500/50'
                                    : 'bg-[#0B0F17] border-[#243045]'
                                }`}>
                                  <div className="text-[11px] text-slate-400">
                                    Итого на объем {quantity} {offer.unit}:
                                  </div>
                                  <div className="flex items-baseline justify-between mt-1">
                                    <span className="font-mono text-white font-semibold">
                                      {formatTenge(offer.offered_price * quantity)}
                                    </span>
                                    <span
                                      className={`font-mono font-bold ${
                                        cardDiff > 0
                                          ? 'text-emerald-400'
                                          : cardDiff < 0
                                          ? 'text-rose-400'
                                          : 'text-slate-400'
                                      }`}
                                    >
                                      {cardDiff > 0
                                        ? `−${formatTenge(cardDiff)}`
                                        : cardDiff < 0
                                        ? `+${formatTenge(Math.abs(cardDiff))}`
                                        : '0 ₸'}
                                    </span>
                                  </div>
                                  {offer.delivery_cost > 0 && (
                                    <div className="text-[10px] text-slate-500 mt-1">
                                      С учетом доставки: {formatTenge(cardDiff - offer.delivery_cost)} разница
                                    </div>
                                  )}
                                </div>

                                {/* Selection Button */}
                                <div className="mt-3">
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setSelectedOfferSupplierId(offer.supplier_id);
                                    }}
                                    className={`w-full py-1.5 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition ${
                                      isSelected
                                        ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20'
                                        : 'bg-[#0B0F17] hover:bg-[#1E293B] border border-[#243045] text-slate-300'
                                    }`}
                                  >
                                    {isSelected ? (
                                      <>
                                        <CheckCircle className="w-3.5 h-3.5" />
                                        <span>Выбрано в расчете</span>
                                      </>
                                    ) : (
                                      <span>Выбрать для расчета</span>
                                    )}
                                  </button>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              ) : null}
            </>
          )}
        </div>
      )}

      {/* TAB 2: SUPPLIER CATALOG */}
      {activeTab === 'catalog' && (
        <div className="space-y-6">
          {/* Explanation Banner */}
          <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-indigo-950/40 to-slate-900/60 border border-indigo-500/30 flex items-start gap-4">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div className="space-y-1 text-xs">
              <h4 className="font-bold text-white text-sm">
                Демонстрационный каталог и пользовательские поставщики
              </h4>
              <p className="text-slate-300 leading-relaxed">
                <strong className="text-indigo-300">База BizMind</strong> предоставляет готовый набор проверенных поставщиков (кофе, молоко, сиропы, посуда, хозтовары). Эти поставщики доступны всем организациям для бенчмаркинга и защищены от случайного удаления арендатором.
              </p>
              <p className="text-slate-400 leading-relaxed">
                <strong className="text-cyan-300">Импортированные поставщики</strong> создаются в вашей организации при загрузке прайс-листов и не видны другим компаниям.
              </p>
            </div>
          </div>

          {/* Controls: Search + Origin Filters */}
          <div className="p-4 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
            {/* Search */}
            <div className="relative w-full md:w-96">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Поиск по названию, контакту, телефону..."
                value={supplierSearch}
                onChange={(e) => setSupplierSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Filter pills */}
            <div className="flex flex-wrap items-center gap-1.5">
              <button
                onClick={() => setSupplierSourceFilter('all')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  supplierSourceFilter === 'all'
                    ? 'bg-slate-700 text-white shadow-sm'
                    : 'bg-[#0B0F17] border border-[#243045] text-slate-400 hover:text-white'
                }`}
              >
                Все ({suppliers.length})
              </button>
              <button
                onClick={() => setSupplierSourceFilter('global')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
                  supplierSourceFilter === 'global'
                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-sm'
                    : 'bg-[#0B0F17] border border-[#243045] text-slate-400 hover:text-white'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Из базы BizMind ({globalSuppliersCount})
              </button>
              <button
                onClick={() => setSupplierSourceFilter('imported')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
                  supplierSourceFilter === 'imported'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'bg-[#0B0F17] border border-[#243045] text-slate-400 hover:text-white'
                }`}
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-cyan-400" />
                Импортированные ({importedSuppliersCount})
              </button>
              <button
                onClick={() => setSupplierSourceFilter('manual')}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition ${
                  supplierSourceFilter === 'manual'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                    : 'bg-[#0B0F17] border border-[#243045] text-slate-400 hover:text-white'
                }`}
              >
                <User className="w-3.5 h-3.5 text-amber-400" />
                Вручную ({manualSuppliersCount})
              </button>

              <button
                onClick={fetchSuppliers}
                className="p-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-slate-400 hover:text-white transition ml-1"
                title="Обновить список"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Supplier Grid */}
          {catalogLoading ? (
            <div className="p-16 text-center text-slate-400 text-xs">
              Загрузка каталога поставщиков...
            </div>
          ) : filteredSuppliers.length === 0 ? (
            <div className="p-12 rounded-2xl bg-[#161F30] border border-[#243045] text-center text-slate-400 text-xs">
              Поставщики не найдены. Измените параметры поиска или фильтрации.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredSuppliers.map((s) => {
                const isGlobal = s.is_global || s.source_type === 'global';
                return (
                  <div
                    key={s.id}
                    className={`p-5 rounded-2xl bg-[#161F30] border flex flex-col justify-between transition hover:border-slate-500 ${
                      isGlobal ? 'border-indigo-500/30' : 'border-[#243045]'
                    }`}
                  >
                    <div>
                      {/* Origin Badge */}
                      <div className="flex items-center justify-between mb-3">
                        {isGlobal ? (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1">
                            <Sparkles className="w-3 h-3 text-indigo-400" />
                            Из базы BizMind
                          </span>
                        ) : s.source_type === 'imported' ? (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                            <FileSpreadsheet className="w-3 h-3 text-cyan-400" />
                            Импортирован
                          </span>
                        ) : (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                            <User className="w-3 h-3 text-amber-400" />
                            Вручную
                          </span>
                        )}
                      </div>

                      {/* Name & Contact */}
                      <h4 className="text-base font-bold text-white">
                        {s.name}
                      </h4>

                      <div className="mt-2.5 space-y-1 text-xs text-slate-400">
                        {s.contact_name && (
                          <div className="flex items-center gap-1.5 text-slate-300">
                            <User className="w-3.5 h-3.5 text-slate-500" />
                            {s.contact_name}
                          </div>
                        )}
                        {s.phone && (
                          <div className="flex items-center gap-1.5">
                            <Phone className="w-3.5 h-3.5 text-slate-500" />
                            <span className="font-mono">{s.phone}</span>
                          </div>
                        )}
                        {s.email && (
                          <div className="flex items-center gap-1.5">
                            <Mail className="w-3.5 h-3.5 text-slate-500" />
                            <span>{s.email}</span>
                          </div>
                        )}
                        {s.address && (
                          <div className="text-[11px] text-slate-500 pt-0.5">
                            Адрес: {s.address}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Delivery & Terms Details */}
                    <div className="mt-4 pt-4 border-t border-[#243045] space-y-2 text-xs">
                      <div className="flex items-center justify-between text-slate-300">
                        <span className="text-slate-400 flex items-center gap-1.5">
                          <Box className="w-3.5 h-3.5" /> Мин. заказ:
                        </span>
                        <span className="font-mono font-medium">
                          {s.minimum_order_amount ? formatTenge(s.minimum_order_amount) : 'Без ограничений'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-slate-300">
                        <span className="text-slate-400 flex items-center gap-1.5">
                          <Truck className="w-3.5 h-3.5" /> Доставка:
                        </span>
                        <span className="font-mono font-medium">
                          {s.delivery_cost === 0 ? 'Бесплатно' : s.delivery_cost ? formatTenge(s.delivery_cost) : 'По согласованию'}
                        </span>
                      </div>

                      {s.notes && (
                        <div className="text-[11px] text-slate-500 pt-1">
                          Примечание: {s.notes}
                        </div>
                      )}

                      {/* Footer protection indicator */}
                      <div className="mt-3 pt-2 text-[10px] text-slate-500 border-t border-slate-800/60">
                        {isGlobal ? (
                          <span className="text-indigo-400/80 flex items-center gap-1">
                            <ShieldCheck className="w-3 h-3 text-indigo-400" />
                            Глобальный каталог BizMind (защищен от удаления)
                          </span>
                        ) : (
                          <span className="text-slate-400 flex items-center gap-1">
                            <CheckCircle className="w-3 h-3 text-emerald-400" />
                            Локальный поставщик организации
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
