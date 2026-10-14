import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Wallet,
} from 'lucide-react';
import { FinancialTransaction, FinanceSummary } from '../types';
import { api } from '../services/api';
import { formatTenge, formatDate } from '../utils/formatters';

interface FinancesPageProps {
  onOpenAddModal: () => void;
}

export const FinancesPage: React.FC<FinancesPageProps> = ({ onOpenAddModal }) => {
  const [transactions, setTransactions] = useState<FinancialTransaction[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Все');
  const [selectedType, setSelectedType] = useState('all');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [txs, cats, sum] = await Promise.all([
        api.getFinances({
          search: search || undefined,
          category: selectedCategory !== 'Все' ? selectedCategory : undefined,
          transaction_type: selectedType !== 'all' ? selectedType : undefined,
        }),
        api.getCategories(),
        api.getFinanceSummary(),
      ]);
      setTransactions(txs);
      setCategories(['Все', ...cats]);
      setSummary(sum);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCategory, selectedType]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchData();
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
            <div className="text-xs text-slate-400 mb-1 flex items-center justify-between">
              <span>Совокупные расходы</span>
              <ArrowDownRight className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-xl font-bold font-mono text-white">
              {formatTenge(summary.total_expenses)}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">Все подтвержденные списания</div>
          </div>

          <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
            <div className="text-xs text-slate-400 mb-1 flex items-center justify-between">
              <span>Совокупная выручка</span>
              <ArrowUpRight className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400">
              {formatTenge(summary.total_income)}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">Касса и безналичные оплаты</div>
          </div>

          <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
            <div className="text-xs text-slate-400 mb-1 flex items-center justify-between">
              <span>Чистый операционный результат</span>
              <Wallet className="w-4 h-4 text-cyan-400" />
            </div>
            <div
              className={`text-xl font-bold font-mono ${
                summary.net_profit >= 0 ? 'text-white' : 'text-rose-400'
              }`}
            >
              {formatTenge(summary.net_profit)}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              Маржа: {summary.total_income > 0 ? ((summary.net_profit / summary.total_income) * 100).toFixed(1) : 0}%
            </div>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Поиск по описанию или назначению..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500"
          />
        </form>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Category Select */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs focus:outline-none focus:border-emerald-500"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-[#161F30]">
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Type Toggle */}
          <div className="flex rounded-xl bg-[#0B0F17] p-1 border border-[#243045] text-xs">
            <button
              onClick={() => setSelectedType('all')}
              className={`px-2.5 py-1 rounded-lg transition ${
                selectedType === 'all'
                  ? 'bg-slate-700 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Все
            </button>
            <button
              onClick={() => setSelectedType('expense')}
              className={`px-2.5 py-1 rounded-lg transition ${
                selectedType === 'expense'
                  ? 'bg-rose-500/20 text-rose-300 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Расходы
            </button>
            <button
              onClick={() => setSelectedType('income')}
              className={`px-2.5 py-1 rounded-lg transition ${
                selectedType === 'income'
                  ? 'bg-emerald-500/20 text-emerald-300 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Доходы
            </button>
          </div>

          {/* Add Operation button */}
          <button
            onClick={onOpenAddModal}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md transition ml-auto"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Добавить операцию</span>
          </button>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
        <div className="p-4 border-b border-[#243045] flex items-center justify-between text-xs text-slate-400">
          <span>Найдено операций: <strong className="text-white">{transactions.length}</strong></span>
          <button
            onClick={fetchData}
            className="hover:text-emerald-400 flex items-center gap-1 transition"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Обновить</span>
          </button>
        </div>

        {loading ? (
          <div className="p-16 text-center text-slate-500 text-xs">Загрузка операций...</div>
        ) : transactions.length === 0 ? (
          <div className="p-16 text-center text-slate-500 text-xs">
            Нет операций, удовлетворяющих заданным критериям фильтра.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase tracking-wider bg-[#0F172A]/50">
                  <th className="py-3 px-4 font-medium">Дата</th>
                  <th className="py-3 px-4 font-medium">Описание</th>
                  <th className="py-3 px-4 font-medium">Категория</th>
                  <th className="py-3 px-4 font-medium">Тип</th>
                  <th className="py-3 px-4 font-medium">Источник</th>
                  <th className="py-3 px-4 font-medium text-right">Сумма</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243045]/60 text-slate-300">
                {transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-4 whitespace-nowrap text-slate-400 font-mono text-[11px]">
                      {formatDate(tx.transaction_date)}
                    </td>
                    <td className="py-3 px-4 font-medium text-white max-w-sm">
                      {tx.description}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-slate-800 border border-slate-700 text-slate-300">
                        {tx.category}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          tx.transaction_type === 'income'
                            ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/25'
                            : 'bg-rose-500/15 text-rose-300 border border-rose-500/25'
                        }`}
                      >
                        {tx.transaction_type === 'income' ? 'Доход' : 'Расход'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 text-[11px]">
                      {tx.source.startsWith('import:') ? 'Импорт Excel' : tx.source}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold whitespace-nowrap">
                      <span
                        className={
                          tx.transaction_type === 'income'
                            ? 'text-emerald-400'
                            : 'text-slate-200'
                        }
                      >
                        {tx.transaction_type === 'income' ? '+' : '−'}
                        {formatTenge(tx.amount)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
