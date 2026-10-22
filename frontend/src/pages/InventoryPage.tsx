import React, { useEffect, useState } from 'react';
import {
  Boxes,
  Plus,
  Search,
  Filter,
  Download,
  AlertTriangle,
  CheckCircle2,
  TrendingDown,
  RotateCcw,
  SlidersHorizontal,
  X,
  PackagePlus,
  RefreshCw,
  FileSpreadsheet,
} from 'lucide-react';
import { Product, InventoryMovement, StockAdjustmentData, WriteOffData } from '../types';
import { api } from '../services/api';
import { formatDate } from '../utils/formatters';

export const InventoryPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'balance' | 'movements'>('balance');
  const [products, setProducts] = useState<Product[]>([]);
  const [movements, setMovements] = useState<InventoryMovement[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Все');
  const [selectedMovementType, setSelectedMovementType] = useState('all');

  // Modals
  const [adjustModalProduct, setAdjustModalProduct] = useState<Product | null>(null);
  const [actualStockInput, setActualStockInput] = useState<number>(0);
  const [adjustReason, setAdjustReason] = useState<string>('Плановая инвентаризация');

  const [writeOffModalProduct, setWriteOffModalProduct] = useState<Product | null>(null);
  const [writeOffQtyInput, setWriteOffQtyInput] = useState<number>(1);
  const [writeOffReason, setWriteOffReason] = useState<string>('Порча / истечение срока');

  const [isAddProductModalOpen, setIsAddProductModalOpen] = useState(false);
  const [newProdName, setNewProdName] = useState('');
  const [newProdCategory, setNewProdCategory] = useState('Кофе и зерно');
  const [newProdUnit, setNewProdUnit] = useState('кг');
  const [newProdSku, setNewProdSku] = useState('');
  const [newProdStock, setNewProdStock] = useState<number>(0);
  const [newProdMinStock, setNewProdMinStock] = useState<number>(5);
  const [newProdDescription, setNewProdDescription] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const [prods, moves] = await Promise.all([
        api.getProducts(),
        api.getInventoryMovements({
          movement_type: selectedMovementType !== 'all' ? selectedMovementType : undefined,
        }),
      ]);
      setProducts(prods);
      setMovements(moves);
    } catch (err: any) {
      console.error(err);
      setErrorMessage('Ошибка загрузки складских данных');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedMovementType]);

  const categories = ['Все', ...Array.from(new Set(products.map((p) => p.category)))];

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.sku && p.sku.toLowerCase().includes(search.toLowerCase()));
    const matchesCategory =
      selectedCategory === 'Все' || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const lowStockCount = products.filter(
    (p) => Number(p.current_stock) <= Number(p.minimum_stock)
  ).length;

  const handleOpenAdjust = (p: Product) => {
    setAdjustModalProduct(p);
    setActualStockInput(Number(p.current_stock));
    setAdjustReason('Плановая инвентаризация');
  };

  const handleSaveAdjust = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!adjustModalProduct) return;
    setIsSubmitting(true);
    try {
      const payload: StockAdjustmentData = {
        product_id: adjustModalProduct.id,
        actual_stock: Number(actualStockInput),
        reason: adjustReason,
      };
      await api.adjustStock(payload);
      setAdjustModalProduct(null);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка проведения инвентаризации');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenWriteOff = (p: Product) => {
    setWriteOffModalProduct(p);
    setWriteOffQtyInput(1);
    setWriteOffReason('Порча / истечение срока');
  };

  const handleSaveWriteOff = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!writeOffModalProduct) return;
    setIsSubmitting(true);
    try {
      const payload: WriteOffData = {
        product_id: writeOffModalProduct.id,
        quantity: Number(writeOffQtyInput),
        reason: writeOffReason,
      };
      await api.writeOffStock(payload);
      setWriteOffModalProduct(null);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка списания');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await api.createProduct({
        name: newProdName,
        category: newProdCategory,
        unit: newProdUnit,
        sku: newProdSku || undefined,
        current_stock: Number(newProdStock) || 0,
        minimum_stock: Number(newProdMinStock) || 0,
        description: newProdDescription || undefined,
      });
      setIsAddProductModalOpen(false);
      setNewProdName('');
      setNewProdSku('');
      setNewProdDescription('');
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка создания товара');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getMovementBadge = (type: string) => {
    switch (type) {
      case 'receipt':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            Поступление
          </span>
        );
      case 'write_off':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30">
            Списание
          </span>
        );
      case 'adjustment':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">
            Корректировка
          </span>
        );
      case 'initial':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-700 text-slate-300">
            Начальный остаток
          </span>
        );
      default:
        return <span>{type}</span>;
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Boxes className="w-5 h-5 text-emerald-400" />
            Склад и товарные запасы
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Учет остатков сырья, инвентаризация, фиксация брака и прозрачный аудит движений
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {/* Export Dropdown / Link */}
          <a
            href={api.getInventoryExportUrl('excel')}
            download
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#161F30] hover:bg-slate-800 border border-[#243045] text-xs text-slate-200 transition"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>Excel</span>
          </a>
          <a
            href={api.getInventoryExportUrl('csv')}
            download
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#161F30] hover:bg-slate-800 border border-[#243045] text-xs text-slate-200 transition"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-cyan-400" />
            <span>CSV</span>
          </a>
          <button
            onClick={() => setIsAddProductModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md transition"
          >
            <PackagePlus className="w-4 h-4" />
            <span>Новый товар</span>
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs">
          {errorMessage}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Позиций в каталоге</div>
          <div className="text-xl font-bold font-mono text-white">{products.length}</div>
        </div>
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1 flex items-center justify-between">
            <span>В зоне риска / дефицит</span>
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <div
            className={`text-xl font-bold font-mono ${
              lowStockCount > 0 ? 'text-rose-400' : 'text-emerald-400'
            }`}
          >
            {lowStockCount}
          </div>
        </div>
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Операций в журнале</div>
          <div className="text-xl font-bold font-mono text-blue-400">{movements.length}</div>
        </div>
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Состояние учета</div>
          <div className="text-xs font-semibold text-emerald-400 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Согласовано
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[#243045] gap-4">
        <button
          onClick={() => setActiveTab('balance')}
          className={`pb-3 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'balance'
              ? 'border-emerald-500 text-white'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Boxes className="w-4 h-4" />
          <span>Текущие остатки ({products.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('movements')}
          className={`pb-3 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'movements'
              ? 'border-emerald-500 text-white'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span>Журнал движений ({movements.length})</span>
        </button>
      </div>

      {/* Tab 1: Balance Table */}
      {activeTab === 'balance' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="p-3.5 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="relative w-full md:w-80">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Поиск по наименованию или артикулу..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div className="flex items-center gap-2">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs focus:outline-none cursor-pointer"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Table */}
          <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs min-w-[700px]">
                <thead>
                  <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase bg-[#0F172A]/50">
                    <th className="py-3 px-4">Товар</th>
                    <th className="py-3 px-4">Категория</th>
                    <th className="py-3 px-4">Артикул (SKU)</th>
                    <th className="py-3 px-4 text-right">Текущий остаток</th>
                    <th className="py-3 px-4 text-right">Неснижаемый минимум</th>
                    <th className="py-3 px-4 text-center">Статус</th>
                    <th className="py-3 px-4 text-right">Действия</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#243045]/60 text-slate-300">
                  {filteredProducts.map((p) => {
                    const isLow = Number(p.current_stock) <= Number(p.minimum_stock);
                    return (
                      <tr key={p.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3 px-4 font-semibold text-white">{p.name}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded-full text-[10px] bg-slate-800 border border-slate-700 text-slate-300">
                            {p.category}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                          {p.sku || '—'}
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-bold text-white">
                          {p.current_stock} {p.unit}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-slate-400">
                          {p.minimum_stock} {p.unit}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {isLow ? (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30 inline-flex items-center gap-1">
                              <AlertTriangle className="w-2.5 h-2.5" />
                              Дефицит
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                              В норме
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleOpenAdjust(p)}
                              title="Инвентаризация"
                              className="px-2.5 py-1 rounded-lg bg-[#0B0F17] hover:bg-slate-800 text-slate-200 border border-[#243045] text-[11px] flex items-center gap-1 transition"
                            >
                              <RotateCcw className="w-3 h-3 text-cyan-400" />
                              Инвентаризация
                            </button>
                            <button
                              onClick={() => handleOpenWriteOff(p)}
                              title="Списать товар"
                              className="px-2.5 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/25 text-[11px] flex items-center gap-1 transition"
                            >
                              <TrendingDown className="w-3 h-3" />
                              Списать
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Movements Journal */}
      {activeTab === 'movements' && (
        <div className="space-y-4">
          <div className="p-3.5 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Filter className="w-3.5 h-3.5" />
              <span>Тип движения:</span>
              <select
                value={selectedMovementType}
                onChange={(e) => setSelectedMovementType(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs focus:outline-none cursor-pointer"
              >
                <option value="all">Все движения</option>
                <option value="receipt">Поступления (закупки)</option>
                <option value="write_off">Списания (брак / порча)</option>
                <option value="adjustment">Инвентаризации</option>
                <option value="initial">Начальные остатки</option>
              </select>
            </div>
            <button
              onClick={loadData}
              className="hover:text-emerald-400 flex items-center gap-1 text-xs text-slate-400 transition"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Обновить журнал</span>
            </button>
          </div>

          <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs min-w-[700px]">
                <thead>
                  <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase bg-[#0F172A]/50">
                    <th className="py-3 px-4">Дата / Время</th>
                    <th className="py-3 px-4">Товар</th>
                    <th className="py-3 px-4">Тип операции</th>
                    <th className="py-3 px-4 text-right">Изменение</th>
                    <th className="py-3 px-4 text-right">Остаток после</th>
                    <th className="py-3 px-4">Основание / Причина</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#243045]/60 text-slate-300">
                  {movements.map((m) => {
                    const isPositive = m.quantity > 0;
                    return (
                      <tr key={m.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3 px-4 whitespace-nowrap text-slate-400 font-mono text-[11px]">
                          {formatDate(m.created_at)}
                        </td>
                        <td className="py-3 px-4 font-semibold text-white">{m.product_name}</td>
                        <td className="py-3 px-4">{getMovementBadge(m.movement_type)}</td>
                        <td
                          className={`py-3 px-4 text-right font-mono font-bold ${
                            isPositive ? 'text-emerald-400' : 'text-rose-400'
                          }`}
                        >
                          {isPositive ? `+${m.quantity}` : m.quantity}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-slate-200">
                          {m.stock_after}
                        </td>
                        <td className="py-3 px-4 text-slate-400 text-[11px]">
                          {m.reason || '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Adjust Modal */}
      {adjustModalProduct && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#243045] pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <RotateCcw className="w-4 h-4 text-cyan-400" />
                Инвентаризация: {adjustModalProduct.name}
              </h3>
              <button
                onClick={() => setAdjustModalProduct(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveAdjust} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">
                  Фактический фактический остаток ({adjustModalProduct.unit}) *
                </label>
                <input
                  type="number"
                  step="any"
                  min="0"
                  value={actualStockInput}
                  onChange={(e) => setActualStockInput(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white font-mono text-sm focus:outline-none focus:border-emerald-500"
                  required
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Текущий в базе: {adjustModalProduct.current_stock} {adjustModalProduct.unit}.
                  Разница:{' '}
                  {(Number(actualStockInput) - Number(adjustModalProduct.current_stock)).toFixed(2)}
                </span>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Причина корректировки *</label>
                <input
                  type="text"
                  value={adjustReason}
                  onChange={(e) => setAdjustReason(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setAdjustModalProduct(null)}
                  className="px-4 py-2 rounded-xl bg-[#0B0F17] hover:bg-slate-800 text-slate-300"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold"
                >
                  {isSubmitting ? 'Сохранение...' : 'Зафиксировать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Write-off Modal */}
      {writeOffModalProduct && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#243045] pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-rose-400" />
                Списание товара: {writeOffModalProduct.name}
              </h3>
              <button
                onClick={() => setWriteOffModalProduct(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveWriteOff} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">
                  Количество к списанию ({writeOffModalProduct.unit}) *
                </label>
                <input
                  type="number"
                  step="any"
                  min="0.01"
                  max={Number(writeOffModalProduct.current_stock)}
                  value={writeOffQtyInput}
                  onChange={(e) => setWriteOffQtyInput(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white font-mono text-sm focus:outline-none focus:border-rose-500"
                  required
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Доступно на складе: {writeOffModalProduct.current_stock} {writeOffModalProduct.unit}
                </span>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Основание / Причина списания *</label>
                <select
                  value={writeOffReason}
                  onChange={(e) => setWriteOffReason(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-rose-500"
                >
                  <option value="Порча / истечение срока">Порча / истечение срока</option>
                  <option value="Производственный брак / бой">Производственный брак / бой</option>
                  <option value="Проработка / калибровка рецептуры">Проработка / калибровка рецептуры</option>
                  <option value="Угощение / представительские расходы">Угощение / представительские расходы</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setWriteOffModalProduct(null)}
                  className="px-4 py-2 rounded-xl bg-[#0B0F17] hover:bg-slate-800 text-slate-300"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-400 text-white font-bold"
                >
                  {isSubmitting ? 'Списание...' : 'Списать со склада'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {isAddProductModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-lg p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#243045] pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <PackagePlus className="w-4 h-4 text-emerald-400" />
                Новый товар в каталоге
              </h3>
              <button
                onClick={() => setIsAddProductModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateProduct} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Наименование товара *</label>
                <input
                  type="text"
                  placeholder="Например: Сироп Карамель 1л"
                  value={newProdName}
                  onChange={(e) => setNewProdName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Категория *</label>
                  <input
                    type="text"
                    value={newProdCategory}
                    onChange={(e) => setNewProdCategory(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Единица измерения *</label>
                  <select
                    value={newProdUnit}
                    onChange={(e) => setNewProdUnit(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="кг">кг</option>
                    <option value="л">л</option>
                    <option value="шт">шт</option>
                    <option value="упак">упак</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Артикул / SKU</label>
                  <input
                    type="text"
                    placeholder="SYR-CRM-01"
                    value={newProdSku}
                    onChange={(e) => setNewProdSku(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Начальный остаток</label>
                  <input
                    type="number"
                    step="any"
                    value={newProdStock}
                    onChange={(e) => setNewProdStock(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Мин. остаток</label>
                  <input
                    type="number"
                    step="any"
                    value={newProdMinStock}
                    onChange={(e) => setNewProdMinStock(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Описание / Заметка</label>
                <textarea
                  rows={2}
                  value={newProdDescription}
                  onChange={(e) => setNewProdDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddProductModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#0B0F17] hover:bg-slate-800 text-slate-300"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold"
                >
                  {isSubmitting ? 'Создание...' : 'Создать товар'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default InventoryPage;
