import React, { useEffect, useState } from 'react';
import {
  ShoppingBag,
  Plus,
  Search,
  Filter,
  CheckCircle,
  Clock,
  PackageCheck,
  Ban,
  FileText,
  ChevronDown,
  ChevronUp,
  X,
  Trash2,
  Copy,
  Printer,
  Calendar,
  Building2,
  Truck,
} from 'lucide-react';
import { PurchaseOrder, Supplier, Product, CreatePurchaseOrderData } from '../types';
import { api } from '../services/api';
import { formatTenge, formatDate } from '../utils/formatters';
import { formatApiError } from '../utils/error';

interface OrdersPageProps {
  onRefreshAux?: () => void;
}

export const OrdersPage: React.FC<OrdersPageProps> = () => {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null);

  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [docModalContent, setDocModalContent] = useState<{ title: string; text: string } | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // New Order Form state
  const [newOrderSupplierId, setNewOrderSupplierId] = useState<number>(0);
  const [newOrderDate, setNewOrderDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [newOrderDeliveryDate, setNewOrderDeliveryDate] = useState<string>('');
  const [newOrderDeliveryCost, setNewOrderDeliveryCost] = useState<number>(0);
  const [newOrderNotes, setNewOrderNotes] = useState<string>('');
  const [newOrderItems, setNewOrderItems] = useState<
    { product_id: number; quantity: number; unit_price: number }[]
  >([]);

  const loadData = async () => {
    setLoading(true);
    setActionError(null);
    try {
      const [ordList, supList, prodList] = await Promise.all([
        api.getOrders({
          status: statusFilter !== 'all' ? statusFilter : undefined,
        }),
        api.getSuppliers(),
        api.getProducts(),
      ]);
      setOrders(ordList);
      setSuppliers(supList);
      setProducts(prodList);
      if (supList.length > 0 && newOrderSupplierId === 0) {
        setNewOrderSupplierId(supList[0].id);
        setNewOrderDeliveryCost(supList[0].delivery_cost || 0);
      }
    } catch (err: any) {
      console.error(err);
      setActionError('Ошибка загрузки данных заказов');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleSupplierChange = (supId: number) => {
    setNewOrderSupplierId(supId);
    const sup = suppliers.find((s) => s.id === supId);
    if (sup) {
      setNewOrderDeliveryCost(sup.delivery_cost || 0);
    }
  };

  const handleAddItem = () => {
    if (products.length === 0) return;
    const firstProd = products[0];
    setNewOrderItems((prev) => [
      ...prev,
      {
        product_id: firstProd.id,
        quantity: 1,
        unit_price: 1000,
      },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setNewOrderItems((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleItemChange = (
    index: number,
    field: 'product_id' | 'quantity' | 'unit_price',
    value: number
  ) => {
    setNewOrderItems((prev) =>
      prev.map((item, idx) => (idx === index ? { ...item, [field]: value } : item))
    );
  };

  const calculateSubtotal = () => {
    return newOrderItems.reduce((acc, it) => acc + (it.quantity || 0) * (it.unit_price || 0), 0);
  };

  const calculateTotal = () => {
    return calculateSubtotal() + (Number(newOrderDeliveryCost) || 0);
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newOrderItems.length === 0) {
      setActionError('Добавьте хотя бы один товар в заказ');
      return;
    }
    if (!newOrderSupplierId) {
      setActionError('Выберите поставщика');
      return;
    }

    setIsSubmitting(true);
    setActionError(null);
    try {
      const payload: CreatePurchaseOrderData = {
        supplier_id: newOrderSupplierId,
        order_date: newOrderDate,
        expected_delivery_date: newOrderDeliveryDate || undefined,
        delivery_cost: Number(newOrderDeliveryCost) || 0,
        notes: newOrderNotes || undefined,
        items: newOrderItems.map((it) => ({
          product_id: it.product_id,
          ordered_quantity: Number(it.quantity),
          quantity: Number(it.quantity),
          unit_price: Number(it.unit_price),
        })),
      };
      await api.createOrder(payload);
      setIsCreateModalOpen(false);
      setNewOrderItems([]);
      setNewOrderNotes('');
      await loadData();
    } catch (err: any) {
      console.error('Order creation error:', err);
      setActionError(formatApiError(err, 'Не удалось создать заказ'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirm = async (orderId: number) => {
    try {
      await api.confirmOrder(orderId);
      await loadData();
    } catch (err: any) {
      alert(formatApiError(err, 'Ошибка подтверждения'));
    }
  };

  const handleReceive = async (orderId: number) => {
    if (
      !confirm(
        'Подтвердить приемку поставки?\nТовары будут оприходованы на склад, а сумма заказа отразится в расходах.'
      )
    ) {
      return;
    }
    try {
      await api.receiveOrder(orderId);
      await loadData();
    } catch (err: any) {
      alert(formatApiError(err, 'Ошибка при приемке'));
    }
  };

  const handleCancel = async (orderId: number) => {
    if (!confirm('Отменить заказ?')) return;
    try {
      await api.cancelOrder(orderId);
      await loadData();
    } catch (err: any) {
      alert(formatApiError(err, 'Ошибка отмены'));
    }
  };

  const handleShowDocument = async (order: PurchaseOrder) => {
    try {
      const doc = await api.getOrderDocument(order.id);
      setDocModalContent({
        title: `Накладная заказа ${order.order_number}`,
        text: doc,
      });
    } catch (err: any) {
      alert('Не удалось загрузить документ заказа');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'draft':
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Черновик
          </span>
        );
      case 'confirmed':
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            Подтвержден
          </span>
        );
      case 'received':
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
            <PackageCheck className="w-3 h-3" />
            Поступил на склад
          </span>
        );
      case 'cancelled':
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30 flex items-center gap-1">
            <Ban className="w-3 h-3" />
            Отменен
          </span>
        );
      default:
        return <span>{status}</span>;
    }
  };

  const filteredOrders = orders.filter((o) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      o.order_number.toLowerCase().includes(q) ||
      o.supplier_name.toLowerCase().includes(q) ||
      (o.notes && o.notes.toLowerCase().includes(q))
    );
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-emerald-400" />
            Управление заказами поставщикам
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Формирование черновиков, отправка спецификаций, контроль доставки и оприходование на склад
          </p>
        </div>
        <button
          onClick={() => {
            setIsCreateModalOpen(true);
            if (newOrderItems.length === 0) {
              handleAddItem();
            }
          }}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Сформировать заказ</span>
        </button>
      </div>

      {actionError && (
        <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Всего заказов</div>
          <div className="text-xl font-bold font-mono text-white">{orders.length}</div>
        </div>
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Ожидают поставки</div>
          <div className="text-xl font-bold font-mono text-blue-400">
            {orders.filter((o) => o.status === 'confirmed').length}
          </div>
        </div>
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Черновики</div>
          <div className="text-xl font-bold font-mono text-amber-400">
            {orders.filter((o) => o.status === 'draft').length}
          </div>
        </div>
        <div className="p-4 rounded-xl bg-[#161F30] border border-[#243045]">
          <div className="text-xs text-slate-400 mb-1">Оприходовано</div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {orders.filter((o) => o.status === 'received').length}
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3.5 sm:p-4 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Поиск по номеру или поставщику..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Status Filters */}
        <div className="flex flex-wrap items-center gap-1.5 rounded-xl bg-[#0B0F17] p-1 border border-[#243045] text-xs">
          {[
            { id: 'all', label: 'Все' },
            { id: 'draft', label: 'Черновики' },
            { id: 'confirmed', label: 'Подтвержденные' },
            { id: 'received', label: 'Принятые' },
            { id: 'cancelled', label: 'Отмененные' },
          ].map((st) => (
            <button
              key={st.id}
              onClick={() => setStatusFilter(st.id)}
              className={`px-3 py-1.5 rounded-lg transition ${
                statusFilter === st.id
                  ? 'bg-slate-700 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>
      </div>

      {/* Orders List */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-16 text-center text-slate-500 text-xs rounded-2xl bg-[#161F30] border border-[#243045]">
            Загрузка списка заказов...
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="p-16 text-center text-slate-500 text-xs rounded-2xl bg-[#161F30] border border-[#243045]">
            Заказы не найдены. Нажмите «Сформировать заказ», чтобы создать первую поставку.
          </div>
        ) : (
          filteredOrders.map((order) => {
            const isExpanded = expandedOrderId === order.id;
            return (
              <div
                key={order.id}
                className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden transition"
              >
                <div className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono font-bold text-white text-sm">
                        {order.order_number}
                      </span>
                      {getStatusBadge(order.status)}
                      <span className="text-[11px] text-slate-500 font-mono">
                        от {formatDate(order.order_date)}
                      </span>
                    </div>

                    <div className="text-xs text-slate-300 flex flex-wrap items-center gap-3">
                      <span className="flex items-center gap-1 text-white font-medium">
                        <Building2 className="w-3.5 h-3.5 text-slate-400" />
                        {order.supplier_name}
                      </span>
                      {order.expected_delivery_date && (
                        <span className="flex items-center gap-1 text-slate-400 text-[11px]">
                          <Calendar className="w-3 h-3 text-cyan-400" />
                          Ожидается: {formatDate(order.expected_delivery_date)}
                        </span>
                      )}
                      {order.delivery_cost > 0 && (
                        <span className="flex items-center gap-1 text-slate-400 text-[11px]">
                          <Truck className="w-3 h-3 text-amber-400" />
                          Доставка: {formatTenge(order.delivery_cost)}
                        </span>
                      )}
                    </div>

                    {order.notes && (
                      <p className="text-[11px] text-slate-400 italic">Примечание: {order.notes}</p>
                    )}
                  </div>

                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 md:self-center">
                    <div className="text-left sm:text-right">
                      <div className="text-[11px] text-slate-400">Итоговая сумма</div>
                      <div className="text-lg font-bold font-mono text-emerald-400">
                        {formatTenge(order.total_amount)}
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        onClick={() => handleShowDocument(order)}
                        title="Печатный бланк / накладная"
                        className="px-2.5 py-1.5 rounded-lg bg-[#0B0F17] hover:bg-slate-800 text-slate-300 text-xs border border-[#243045] flex items-center gap-1 transition"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        <span>Бланк</span>
                      </button>

                      {order.status === 'draft' && (
                        <>
                          <button
                            onClick={() => handleConfirm(order.id)}
                            className="px-3 py-1.5 rounded-lg bg-blue-500 hover:bg-blue-400 text-slate-950 font-bold text-xs transition"
                          >
                            Подтвердить
                          </button>
                          <button
                            onClick={() => handleCancel(order.id)}
                            className="px-2.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs border border-rose-500/30 transition"
                          >
                            Отменить
                          </button>
                        </>
                      )}

                      {order.status === 'confirmed' && (
                        <>
                          <button
                            onClick={() => handleReceive(order.id)}
                            className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition flex items-center gap-1 shadow-md shadow-emerald-500/10"
                          >
                            <PackageCheck className="w-3.5 h-3.5" />
                            Принять на склад
                          </button>
                          <button
                            onClick={() => handleCancel(order.id)}
                            className="px-2.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs border border-rose-500/30 transition"
                          >
                            Отменить
                          </button>
                        </>
                      )}

                      <button
                        onClick={() => setExpandedOrderId(isExpanded ? null : order.id)}
                        className="p-1.5 rounded-lg bg-[#0B0F17] hover:bg-slate-800 text-slate-400 text-xs border border-[#243045] transition"
                        title="Показать состав заказа"
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expanded items list */}
                {isExpanded && (
                  <div className="border-t border-[#243045] bg-[#0F172A]/70 p-4">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      Позиции спецификации ({order.items.length})
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs min-w-[500px]">
                        <thead>
                          <tr className="border-b border-[#243045] text-slate-400 text-[10px] uppercase">
                            <th className="py-2 px-3">Товар</th>
                            <th className="py-2 px-3 text-right">Заказано</th>
                            <th className="py-2 px-3 text-right">Цена за ед.</th>
                            <th className="py-2 px-3 text-right">Сумма</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#243045]/50 text-slate-300">
                          {order.items.map((it) => (
                            <tr key={it.id || it.product_id}>
                              <td className="py-2.5 px-3 font-medium text-white">
                                {it.product_name || `Товар #${it.product_id}`}
                              </td>
                              <td className="py-2.5 px-3 text-right font-mono">
                                {it.quantity} {it.unit}
                              </td>
                              <td className="py-2.5 px-3 text-right font-mono text-slate-400">
                                {formatTenge(it.unit_price)}
                              </td>
                              <td className="py-2.5 px-3 text-right font-mono font-bold text-slate-200">
                                {formatTenge(it.total_price)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Create Order Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
            <div className="p-4 sm:p-5 border-b border-[#243045] flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <ShoppingBag className="w-5 h-5 text-emerald-400" />
                Новый заказ поставщику
              </h3>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateOrder} className="p-4 sm:p-6 overflow-y-auto space-y-4 text-xs">
              {/* Supplier & Delivery */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <label className="block text-slate-400 mb-1">Поставщик *</label>
                  <select
                    value={newOrderSupplierId}
                    onChange={(e) => handleSupplierChange(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                    required
                  >
                    {suppliers.map((s) => {
                      const isGlobal = s.is_global || s.source_type === 'global';
                      const originTag = isGlobal ? ' [База BizMind]' : s.source_type === 'imported' ? ' [Импорт]' : '';
                      return (
                        <option key={s.id} value={s.id} className="bg-[#161F30]">
                          {s.name}{originTag} (мин. заказ {formatTenge(s.minimum_order_amount || 0)})
                        </option>
                      );
                    })}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Стоимость доставки (₸)</label>
                  <input
                    type="number"
                    min="0"
                    step="100"
                    value={newOrderDeliveryCost}
                    onChange={(e) => setNewOrderDeliveryCost(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Дата заказа *</label>
                  <input
                    type="date"
                    value={newOrderDate}
                    onChange={(e) => setNewOrderDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Ожидаемая дата поставки</label>
                  <input
                    type="date"
                    value={newOrderDeliveryDate}
                    onChange={(e) => setNewOrderDeliveryDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Примечание к заказу</label>
                <input
                  type="text"
                  placeholder="Например: ворота №2, доставка до 11:00"
                  value={newOrderNotes}
                  onChange={(e) => setNewOrderNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              {/* Items Section */}
              <div className="pt-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-slate-300">Товарные позиции *</span>
                  <button
                    type="button"
                    onClick={handleAddItem}
                    className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 text-[11px] font-semibold flex items-center gap-1 transition"
                  >
                    <Plus className="w-3 h-3" />
                    Добавить строку
                  </button>
                </div>

                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {newOrderItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-[#0B0F17] border border-[#243045] flex flex-col sm:flex-row items-stretch sm:items-center gap-2"
                    >
                      <div className="flex-1">
                        <select
                          value={item.product_id}
                          onChange={(e) =>
                            handleItemChange(idx, 'product_id', Number(e.target.value))
                          }
                          className="w-full px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs focus:outline-none"
                        >
                          {products.map((p) => (
                            <option key={p.id} value={p.id}>
                              {p.name} ({p.unit})
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="w-full sm:w-28 flex items-center gap-1">
                        <input
                          type="number"
                          min="0.1"
                          step="any"
                          placeholder="Кол-во"
                          value={item.quantity}
                          onChange={(e) =>
                            handleItemChange(idx, 'quantity', Number(e.target.value))
                          }
                          className="w-full px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs font-mono"
                          required
                        />
                      </div>

                      <div className="w-full sm:w-32 flex items-center gap-1">
                        <input
                          type="number"
                          min="0"
                          step="any"
                          placeholder="Цена"
                          value={item.unit_price}
                          onChange={(e) =>
                            handleItemChange(idx, 'unit_price', Number(e.target.value))
                          }
                          className="w-full px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs font-mono"
                          required
                        />
                        <span className="text-[11px] text-slate-500">₸</span>
                      </div>

                      <div className="w-24 text-right font-mono text-emerald-400 font-bold self-center">
                        {formatTenge((item.quantity || 0) * (item.unit_price || 0))}
                      </div>

                      <button
                        type="button"
                        onClick={() => handleRemoveItem(idx)}
                        className="text-slate-500 hover:text-rose-400 p-1 self-center"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Totals Box */}
              <div className="p-3.5 rounded-xl bg-[#0F172A] border border-[#243045] flex items-center justify-between font-mono">
                <span className="text-slate-400">Итого с доставкой:</span>
                <span className="text-base font-bold text-emerald-400">
                  {formatTenge(calculateTotal())}
                </span>
              </div>

              {/* Buttons */}
              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#0B0F17] hover:bg-slate-800 text-slate-300 transition"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition disabled:opacity-50"
                >
                  {isSubmitting ? 'Сохранение...' : 'Создать черновик'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document View Modal */}
      {docModalContent && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b border-[#243045] flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                {docModalContent.title}
              </h3>
              <button
                onClick={() => setDocModalContent(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 overflow-y-auto flex-1 font-mono text-xs text-slate-200 bg-[#0B0F17] whitespace-pre-wrap select-all m-4 rounded-xl border border-[#243045]">
              {docModalContent.text}
            </div>

            <div className="p-4 border-t border-[#243045] flex justify-end gap-3">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(docModalContent.text);
                  alert('Текст накладной скопирован в буфер обмена');
                }}
                className="px-3 py-1.5 rounded-lg bg-[#0B0F17] hover:bg-slate-800 text-slate-200 border border-[#243045] text-xs flex items-center gap-1.5 transition"
              >
                <Copy className="w-3.5 h-3.5" />
                Копировать
              </button>
              <button
                onClick={() => window.print()}
                className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition"
              >
                <Printer className="w-3.5 h-3.5" />
                Печать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default OrdersPage;
