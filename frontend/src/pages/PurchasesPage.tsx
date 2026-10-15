import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  ShoppingBag,
  TrendingUp,
  ArrowRight,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';
import { Purchase, Supplier } from '../types';
import { api } from '../services/api';
import { formatTenge, formatDate } from '../utils/formatters';
import { ProductHistoryModal } from '../components/ProductHistoryModal';

interface PurchasesPageProps {
  initialProductId?: number | null;
  onGoToComparison: (productId: number) => void;
}

export const PurchasesPage: React.FC<PurchasesPageProps> = ({
  initialProductId,
  onGoToComparison,
}) => {
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedSupplier, setSelectedSupplier] = useState<string>('all');
  const [historyModalProductId, setHistoryModalProductId] = useState<number | null>(
    initialProductId || null
  );

  const fetchData = async () => {
    setLoading(true);
    try {
      const [pData, sData] = await Promise.all([
        api.getPurchases({
          search: search || undefined,
          supplier_id: selectedSupplier !== 'all' ? Number(selectedSupplier) : undefined,
        }),
        api.getSuppliers(),
      ]);
      setPurchases(pData);
      setSuppliers(sData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedSupplier]);

  const totalSpent = purchases.reduce((acc, p) => acc + p.total_price, 0);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6 max-w-7xl mx-auto">
      {/* Product History Modal if opened */}
      <ProductHistoryModal
        productId={historyModalProductId}
        onClose={() => setHistoryModalProductId(null)}
        onGoToComparison={onGoToComparison}
      />

      {/* Header Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Всего закуплено на сумму</div>
          <div className="text-xl font-bold font-mono text-white">
            {formatTenge(totalSpent)}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">По всем позициям из истории</div>
        </div>

        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Количество закупок</div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {purchases.length} партий
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Отражено в базе данных</div>
        </div>

        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Ключевой сценарий</div>
          <div className="text-sm font-bold text-amber-300 mt-1">
            Кофе Espresso Blend (+15%)
          </div>
          <button
            onClick={() => setHistoryModalProductId(1)}
            className="text-[11px] text-emerald-400 hover:text-emerald-300 font-semibold mt-1 flex items-center gap-1"
          >
            Посмотреть график цен →
          </button>
        </div>
      </div>

      {/* Filters and search */}
      <div className="p-3.5 sm:p-4 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        {/* Search */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetchData();
          }}
          className="relative w-full md:w-80"
        >
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Поиск по товару или поставщику..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500"
          />
        </form>

        {/* Supplier Filter */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <select
            value={selectedSupplier}
            onChange={(e) => setSelectedSupplier(e.target.value)}
            className="w-full md:w-auto px-3 py-1.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs focus:outline-none focus:border-emerald-500 cursor-pointer"
          >
            <option value="all">Все поставщики</option>
            {suppliers.map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </select>

          <button
            onClick={fetchData}
            className="p-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-slate-400 hover:text-white transition shrink-0"
            title="Обновить"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Purchases Table */}
      <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
        <div className="p-4 border-b border-[#243045] flex items-center justify-between text-xs text-slate-400">
          <span>
            Показано поставок: <strong className="text-white">{purchases.length}</strong> (кликните по строке для просмотра динамики цены)
          </span>
        </div>

        {loading ? (
          <div className="p-16 text-center text-slate-500 text-xs">Загрузка истории закупок...</div>
        ) : purchases.length === 0 ? (
          <div className="p-16 text-center text-slate-500 text-xs">Закупок не найдено.</div>
        ) : (
          <div className="overflow-x-auto -mx-4 sm:mx-0 px-4 sm:px-0">
            <table className="w-full text-left text-xs min-w-[700px]">
              <thead>
                <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase tracking-wider bg-[#0F172A]/50">
                  <th className="py-3 px-4 font-medium">Товар</th>
                  <th className="py-3 px-4 font-medium">Категория</th>
                  <th className="py-3 px-4 font-medium">Поставщик</th>
                  <th className="py-3 px-4 font-medium">Дата закупки</th>
                  <th className="py-3 px-4 font-medium text-right">Объем</th>
                  <th className="py-3 px-4 font-medium text-right">Цена за ед.</th>
                  <th className="py-3 px-4 font-medium text-right">Сумма</th>
                  <th className="py-3 px-4 font-medium text-center">Анализ</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243045]/60 text-slate-300">
                {purchases.map((p) => {
                  const isCoffeeSpike =
                    p.product_id === 1 && p.unit_price === 11500;
                  return (
                    <tr
                      key={p.id}
                      onClick={() => setHistoryModalProductId(p.product_id)}
                      className={`hover:bg-slate-800/40 cursor-pointer transition ${
                        isCoffeeSpike ? 'bg-rose-950/20' : ''
                      }`}
                    >
                      <td className="py-3 px-4 font-semibold text-white">
                        <div className="flex items-center gap-2">
                          <span>{p.product_name}</span>
                          {isCoffeeSpike && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                              +15%
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-400">{p.product_category}</td>
                      <td className="py-3 px-4 text-slate-300">{p.supplier_name}</td>
                      <td className="py-3 px-4 whitespace-nowrap text-slate-400 font-mono text-[11px]">
                        {formatDate(p.purchase_date)}
                      </td>
                      <td className="py-3 px-4 text-right font-mono">
                        {p.quantity} {p.unit}
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-white">
                        {formatTenge(p.unit_price)}
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-emerald-400">
                        {formatTenge(p.total_price)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="p-1 rounded text-slate-400 hover:text-emerald-400 transition inline-block">
                          <TrendingUp className="w-4 h-4" />
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
