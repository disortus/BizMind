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
  Edit3,
  Lock,
  AlertTriangle,
  Info,
  RefreshCw,
} from 'lucide-react';
import {
  PurchaseOrder,
  Supplier,
  Product,
  CreatePurchaseOrderData,
  UpdatePurchaseOrderData,
  SupplierCatalogItem,
} from '../types';
import { api } from '../services/api';
import { formatTenge, formatDate } from '../utils/formatters';
import { formatApiError } from '../utils/error';

interface OrdersPageProps {
  onRefreshAux?: () => void;
  prefillOrder?: {
    supplierId?: number;
    productId?: number;
    quantity?: number;
    unitPrice?: number;
  } | null;
  onClearPrefill?: () => void;
}

export const OrdersPage: React.FC<OrdersPageProps> = ({
  onRefreshAux,
  prefillOrder,
  onClearPrefill,
}) => {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null);

  // Modal & form states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<PurchaseOrder | null>(null);
  const [docModalContent, setDocModalContent] = useState<{ title: string; text: string } | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Supplier Catalog
  const [supplierCatalog, setSupplierCatalog] = useState<SupplierCatalogItem[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(false);

  // Order Form fields
  const [orderSupplierId, setOrderSupplierId] = useState<number>(0);
  const [orderDate, setOrderDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [orderDeliveryDate, setOrderDeliveryDate] = useState<string>('');
  const [orderDeliveryCost, setOrderDeliveryCost] = useState<number>(0);
  const [orderNotes, setOrderNotes] = useState<string>('');
  const [orderItems, setOrderItems] = useState<
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
      if (supList.length > 0 && orderSupplierId === 0) {
        setOrderSupplierId(supList[0].id);
        setOrderDeliveryCost(supList[0].delivery_cost || 0);
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

  // Load catalog for a specific supplier
  const fetchCatalog = async (supId: number): Promise<SupplierCatalogItem[]> => {
    if (!supId) {
      setSupplierCatalog([]);
      return [];
    }
    setCatalogLoading(true);
    try {
      const items = await api.getSupplierCatalog(supId);
      setSupplierCatalog(items);
      return items;
    } catch (err) {
      console.error('Failed to load supplier catalog', err);
      setSupplierCatalog([]);
      return [];
    } finally {
      setCatalogLoading(false);
    }
  };

  // Handle pre-fill from ComparisonPage
  useEffect(() => {
    if (prefillOrder && prefillOrder.supplierId) {
      const targetSupId = prefillOrder.supplierId;
      setEditingOrder(null);
      setOrderSupplierId(targetSupId);
      const sup = suppliers.find((s) => s.id === targetSupId);
      if (sup) {
        setOrderDeliveryCost(sup.delivery_cost || 0);
      }
      setOrderDate(new Date().toISOString().split('T')[0]);
      setOrderDeliveryDate('');
      setOrderNotes('');
      setIsModalOpen(true);

      fetchCatalog(targetSupId).then((catalog) => {
        if (prefillOrder.productId) {
          const catItem = catalog.find((c) => c.product_id === prefillOrder.productId);
          const price = catItem ? catItem.unit_price : (prefillOrder.unitPrice || 0);
          setOrderItems([
            {
              product_id: prefillOrder.productId,
              quantity: prefillOrder.quantity || 1,
              unit_price: price,
            },
          ]);
        } else if (catalog.length > 0) {
          setOrderItems([
            {
              product_id: catalog[0].product_id,
              quantity: Math.max(1, catalog[0].minimum_order_quantity || 1),
              unit_price: catalog[0].unit_price,
            },
          ]);
        }
      });

      onClearPrefill?.();
    }
  }, [prefillOrder, suppliers]);

  const handleOpenCreateModal = async () => {
    setEditingOrder(null);
    setActionError(null);
    const supId = orderSupplierId || (suppliers[0]?.id ?? 0);
    setOrderSupplierId(supId);
    const sup = suppliers.find((s) => s.id === supId);
    setOrderDeliveryCost(sup?.delivery_cost || 0);
    setOrderDate(new Date().toISOString().split('T')[0]);
    setOrderDeliveryDate('');
    setOrderNotes('');
    setIsModalOpen(true);

    const catalog = await fetchCatalog(supId);
    if (catalog.length > 0) {
      setOrderItems([
        {
          product_id: catalog[0].product_id,
          quantity: Math.max(1, catalog[0].minimum_order_quantity || 1),
          unit_price: catalog[0].unit_price,
        },
      ]);
    } else {
      setOrderItems([]);
    }
  };

  const handleOpenEditModal = async (order: PurchaseOrder) => {
    if (order.status !== 'draft') {
      alert('Редактировать можно только заказы в статусе «Черновик»');
      return;
    }
    setEditingOrder(order);
    setActionError(null);
    setOrderSupplierId(order.supplier_id);
    setOrderDeliveryCost(order.delivery_cost || 0);
    setOrderDate(order.order_date);
    setOrderDeliveryDate(order.expected_delivery_date || '');
    setOrderNotes(order.notes || '');
    setIsModalOpen(true);

    const catalog = await fetchCatalog(order.supplier_id);
    if (order.items && order.items.length > 0) {
      setOrderItems(
        order.items.map((it) => {
          const catItem = catalog.find((c) => c.product_id === it.product_id);
          return {
            product_id: it.product_id,
            quantity: it.quantity,
            unit_price: catItem ? catItem.unit_price : it.unit_price,
          };
        })
      );
    } else if (catalog.length > 0) {
      setOrderItems([
        {
          product_id: catalog[0].product_id,
          quantity: 1,
          unit_price: catalog[0].unit_price,
        },
      ]);
    } else {
      setOrderItems([]);
    }
  };

  const handleSupplierChange = async (supId: number) => {
    setOrderSupplierId(supId);
    const sup = suppliers.find((s) => s.id === supId);
    if (sup) {
      setOrderDeliveryCost(sup.delivery_cost || 0);
    }
    const catalog = await fetchCatalog(supId);
    if (catalog.length > 0) {
      setOrderItems([
        {
          product_id: catalog[0].product_id,
          quantity: Math.max(1, catalog[0].minimum_order_quantity || 1),
          unit_price: catalog[0].unit_price,
        },
      ]);
    } else {
      setOrderItems([]);
    }
  };

  const handleAddItem = () => {
    if (supplierCatalog.length === 0) return;
    const existingIds = new Set(orderItems.map((it) => it.product_id));
    const available = supplierCatalog.find((c) => !existingIds.has(c.product_id)) || supplierCatalog[0];
    setOrderItems((prev) => [
      ...prev,
      {
        product_id: available.product_id,
        quantity: Math.max(1, available.minimum_order_quantity || 1),
        unit_price: available.unit_price,
      },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setOrderItems((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleItemProductChange = (index: number, newProductId: number) => {
    const catItem = supplierCatalog.find((c) => c.product_id === newProductId);
    const price = catItem ? catItem.unit_price : 0;
    setOrderItems((prev) =>
      prev.map((item, idx) =>
        idx === index
          ? {
              ...item,
              product_id: newProductId,
              unit_price: price,
              quantity:
                catItem && item.quantity < (catItem.minimum_order_quantity || 1)
                  ? catItem.minimum_order_quantity || 1
                  : item.quantity,
            }
          : item
      )
    );
  };

  const handleItemQuantityChange = (index: number, qty: number) => {
    setOrderItems((prev) =>
      prev.map((item, idx) => (idx === index ? { ...item, quantity: qty } : item))
    );
  };

  const calculateSubtotal = () => {
    return orderItems.reduce((acc, it) => acc + (it.quantity || 0) * (it.unit_price || 0), 0);
  };

  const calculateTotal = () => {
    return calculateSubtotal() + (Number(orderDeliveryCost) || 0);
  };

  const selectedSupplier = suppliers.find((s) => s.id === orderSupplierId);
  const minOrderAmount = selectedSupplier?.minimum_order_amount || 0;
  const currentSubtotal = calculateSubtotal();
  const isBelowMinOrder = minOrderAmount > 0 && currentSubtotal < minOrderAmount;
  const missingOrderAmount = Math.max(0, minOrderAmount - currentSubtotal);

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (orderItems.length === 0) {
      setActionError('Добавьте хотя бы один товар в заказ');
      return;
    }
    if (!orderSupplierId) {
      setActionError('Выберите поставщика');
      return;
    }
    if (isBelowMinOrder) {
      setActionError(
        `Минимальная сумма закупки у поставщика «${selectedSupplier?.name}» составляет ${formatTenge(
          minOrderAmount
        )}. Не хватает ${formatTenge(missingOrderAmount)}.`
      );
      return;
    }

    setIsSubmitting(true);
    setActionError(null);
    try {
      const itemsPayload = orderItems.map((it) => ({
        product_id: it.product_id,
        ordered_quantity: Number(it.quantity),
        quantity: Number(it.quantity),
        unit_price: Number(it.unit_price),
      }));

      if (editingOrder) {
        const updatePayload: UpdatePurchaseOrderData = {
          supplier_id: orderSupplierId,
          order_date: orderDate,
          expected_delivery_date: orderDeliveryDate || undefined,
          delivery_cost: Number(orderDeliveryCost) || 0,
          notes: orderNotes || undefined,
          items: itemsPayload,
        };
        await api.updateOrder(editingOrder.id, updatePayload);
      } else {
        const createPayload: CreatePurchaseOrderData = {
          supplier_id: orderSupplierId,
          order_date: orderDate,
          expected_delivery_date: orderDeliveryDate || undefined,
          delivery_cost: Number(orderDeliveryCost) || 0,
          notes: orderNotes || undefined,
          items: itemsPayload,
        };
        await api.createOrder(createPayload);
      }

      setIsModalOpen(false);
      setEditingOrder(null);
      setOrderItems([]);
      setOrderNotes('');
      await loadData();
      onRefreshAux?.();
    } catch (err: any) {
      console.error('Order save error:', err);
      setActionError(formatApiError(err, 'Не удалось сохранить заказ'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirm = async (orderId: number) => {
    try {
      await api.confirmOrder(orderId);
      await loadData();
      onRefreshAux?.();
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
      onRefreshAux?.();
    } catch (err: any) {
      alert(formatApiError(err, 'Ошибка при приемке'));
    }
  };

  const handleCancel = async (orderId: number) => {
    if (!confirm('Отменить заказ?')) return;
    try {
      await api.cancelOrder(orderId);
      await loadData();
      onRefreshAux?.();
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
            Формирование спецификаций по прайс-листам поставщиков, контроль минимальной партии и складская приемка
          </p>
        </div>
        <button
          onClick={handleOpenCreateModal}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Сформировать заказ</span>
        </button>
      </div>

      {actionError && (
        <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between gap-2">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} className="text-rose-400 hover:text-white">
            <X className="w-4 h-4 shrink-0" />
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
            { id: 'received', label: 'Оприходовано' },
            { id: 'cancelled', label: 'Отмененные' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                statusFilter === tab.id
                  ? 'bg-emerald-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Orders List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-16 text-center text-slate-400 text-xs">
            Загрузка журнала заказов...
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="p-12 sm:p-16 rounded-2xl bg-[#161F30] border border-[#243045] text-center space-y-3">
            <ShoppingBag className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-base font-bold text-white">Заказы не найдены</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              По выбранным критериям или статусу заказов нет. Вы можете сформировать новый заказ поставщику с помощью кнопки выше.
            </p>
          </div>
        ) : (
          filteredOrders.map((order) => {
            const isExpanded = expandedOrderId === order.id;

            return (
              <div
                key={order.id}
                className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden transition-all hover:border-slate-600"
              >
                {/* Main Card Header */}
                <div className="p-4 sm:p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono font-bold text-white text-sm">
                        {order.order_number}
                      </span>
                      {getStatusBadge(order.status)}
                      <span className="text-slate-400 text-xs flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {formatDate(order.order_date)}
                      </span>
                    </div>

                    <div className="text-xs text-slate-300 flex flex-wrap items-center gap-x-4 gap-y-1 pt-0.5">
                      <span className="flex items-center gap-1.5 font-medium text-white">
                        <Building2 className="w-3.5 h-3.5 text-emerald-400" />
                        {order.supplier_name}
                      </span>
                      {order.expected_delivery_date && (
                        <span className="text-slate-400 flex items-center gap-1 text-[11px]">
                          <Truck className="w-3 h-3 text-cyan-400" />
                          Ожидается: {formatDate(order.expected_delivery_date)}
                        </span>
                      )}
                    </div>

                    {order.notes && (
                      <p className="text-[11px] text-slate-400 italic">
                        Примечание: {order.notes}
                      </p>
                    )}
                  </div>

                  {/* Right side: sums & action buttons */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between lg:justify-end gap-3 pt-3 lg:pt-0 border-t lg:border-t-0 border-[#243045]">
                    <div className="text-left sm:text-right">
                      <div className="text-base font-bold font-mono text-emerald-400">
                        {formatTenge(order.total_amount)}
                      </div>
                      <div className="text-[11px] text-slate-400">
                        {order.items.length} поз.
                        {order.delivery_cost > 0 && ` (доставка ${formatTenge(order.delivery_cost)})`}
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
                            onClick={() => handleOpenEditModal(order)}
                            className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-semibold border border-amber-500/40 transition flex items-center gap-1"
                            title="Редактировать позиции и параметры черновика"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                            <span>Изменить</span>
                          </button>
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
                            <th className="py-2 px-3 text-right">Фиксированная цена</th>
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

      {/* Create / Edit Order Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-2xl max-h-[92vh] flex flex-col shadow-2xl animate-scaleIn">
            {/* Modal Header */}
            <div className="p-4 sm:p-5 border-b border-[#243045] flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <ShoppingBag className="w-5 h-5 text-emerald-400" />
                  {editingOrder ? `Редактирование черновика ${editingOrder.order_number}` : 'Новый заказ поставщику'}
                </h3>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Позиции формируются строго по каталогу прайс-листа выбранного поставщика
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitOrder} className="p-4 sm:p-6 overflow-y-auto space-y-4 text-xs">
              {/* Supplier & Delivery Info */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">
                    Поставщик <span className="text-rose-400">*</span>
                  </label>
                  <select
                    value={orderSupplierId}
                    onChange={(e) => handleSupplierChange(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                    required
                  >
                    {suppliers.map((s) => {
                      const isGlobal = s.is_global || s.source_type === 'global';
                      const originTag = isGlobal ? ' [База BizMind]' : s.source_type === 'imported' ? ' [Импорт]' : '';
                      return (
                        <option key={s.id} value={s.id} className="bg-[#161F30]">
                          {s.name}{originTag} {s.minimum_order_amount ? `(мин. ${formatTenge(s.minimum_order_amount)})` : ''}
                        </option>
                      );
                    })}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">Стоимость доставки (₸)</label>
                  <input
                    type="number"
                    min="0"
                    step="100"
                    value={orderDeliveryCost}
                    onChange={(e) => setOrderDeliveryCost(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">
                    Дата заказа <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="date"
                    value={orderDate}
                    onChange={(e) => setOrderDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">Ожидаемая дата поставки</label>
                  <input
                    type="date"
                    value={orderDeliveryDate}
                    onChange={(e) => setOrderDeliveryDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold">Примечание к заказу</label>
                <input
                  type="text"
                  placeholder="Например: доставка до 11:00, разгрузка со стороны двора"
                  value={orderNotes}
                  onChange={(e) => setOrderNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              {/* Items Section */}
              <div className="pt-2">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-300">Товарные позиции поставщика</span>
                    {catalogLoading && (
                      <span className="text-[11px] text-slate-400 flex items-center gap-1">
                        <RefreshCw className="w-3 h-3 animate-spin text-emerald-400" />
                        Загрузка прайс-листа...
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={handleAddItem}
                    disabled={supplierCatalog.length === 0}
                    className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 text-[11px] font-semibold flex items-center gap-1 transition disabled:opacity-40"
                  >
                    <Plus className="w-3 h-3" />
                    Добавить строку
                  </button>
                </div>

                {supplierCatalog.length === 0 && !catalogLoading ? (
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center text-slate-400 text-xs space-y-1">
                    <p className="font-medium text-slate-300">
                      У выбранного поставщика пока нет позиций в каталоге / прайс-листе.
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Выберите другого поставщика или загрузите его прайс-лист в разделе «Импорт данных».
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                    {orderItems.map((item, idx) => {
                      const catItem = supplierCatalog.find((c) => c.product_id === item.product_id);

                      return (
                        <div
                          key={idx}
                          className="p-3 rounded-xl bg-[#0B0F17] border border-[#243045] flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5"
                        >
                          {/* Product select from catalog */}
                          <div className="flex-1">
                            <label className="block text-[10px] text-slate-500 mb-0.5 sm:hidden">
                              Товар из прайс-листа
                            </label>
                            <select
                              value={item.product_id}
                              onChange={(e) =>
                                handleItemProductChange(idx, Number(e.target.value))
                              }
                              className="w-full px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs focus:outline-none focus:border-emerald-500"
                            >
                              {supplierCatalog.map((c) => (
                                <option key={c.product_id} value={c.product_id}>
                                  {c.product_name} ({c.unit}) — {formatTenge(c.unit_price)}
                                </option>
                              ))}
                            </select>
                          </div>

                          {/* Quantity */}
                          <div className="w-full sm:w-28">
                            <label className="block text-[10px] text-slate-500 mb-0.5 sm:hidden">
                              Кол-во
                            </label>
                            <div className="flex items-center gap-1">
                              <input
                                type="number"
                                min="0.1"
                                step="any"
                                placeholder="Кол-во"
                                value={item.quantity}
                                onChange={(e) =>
                                  handleItemQuantityChange(idx, Math.max(0.1, Number(e.target.value)))
                                }
                                className="w-full px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs font-mono focus:outline-none focus:border-emerald-500"
                                required
                              />
                              <span className="text-[11px] text-slate-400 shrink-0">
                                {catItem?.unit || 'ед.'}
                              </span>
                            </div>
                          </div>

                          {/* Locked Price from Price List */}
                          <div className="w-full sm:w-36">
                            <label className="block text-[10px] text-slate-500 mb-0.5 sm:hidden">
                              Цена прайс-листа (фиксированная)
                            </label>
                            <div
                              className="px-2.5 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-emerald-400 font-mono text-xs flex items-center justify-between font-bold"
                              title="Цена фиксирована из действующего прайс-листа поставщика"
                            >
                              <div className="flex items-center gap-1">
                                <Lock className="w-3 h-3 text-slate-500" />
                                <span>{formatTenge(item.unit_price)}</span>
                              </div>
                              <span className="text-[10px] text-slate-500">прайс</span>
                            </div>
                          </div>

                          {/* Total item cost */}
                          <div className="w-24 text-right font-mono text-emerald-400 font-bold self-center">
                            {formatTenge((item.quantity || 0) * (item.unit_price || 0))}
                          </div>

                          {/* Remove button */}
                          <button
                            type="button"
                            onClick={() => handleRemoveItem(idx)}
                            className="text-slate-500 hover:text-rose-400 p-1 self-center transition"
                            title="Удалить позицию"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Minimum Order Amount Warning Banner */}
              {isBelowMinOrder && (
                <div className="p-3.5 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-200 text-xs flex items-start gap-2.5 animate-fadeIn">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <div className="font-bold text-amber-300">
                      Не достигнута минимальная сумма закупки
                    </div>
                    <div className="text-[11px] text-amber-200/90 leading-relaxed">
                      Поставщик <strong>«{selectedSupplier?.name}»</strong> принимает заказы от <strong>{formatTenge(minOrderAmount)}</strong>.
                      Текущая сумма по позициям: <span className="font-mono font-bold text-white">{formatTenge(currentSubtotal)}</span>.
                      Для оформления заказа добавьте товаров еще на <span className="font-mono font-bold text-emerald-300">{formatTenge(missingOrderAmount)}</span>.
                    </div>
                  </div>
                </div>
              )}

              {/* Totals Box */}
              <div className="p-3.5 rounded-xl bg-[#0F172A] border border-[#243045] flex flex-col sm:flex-row sm:items-center justify-between gap-2 font-mono">
                <div className="text-slate-400 text-xs space-y-0.5">
                  <div>
                    Сумма по позициям: <span className="text-white font-semibold">{formatTenge(calculateSubtotal())}</span>
                  </div>
                  {orderDeliveryCost > 0 && (
                    <div className="text-[11px] text-slate-500">
                      Стоимость доставки: {formatTenge(orderDeliveryCost)}
                    </div>
                  )}
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-slate-400 text-xs">Итого к оплате:</span>
                  <span className="text-lg font-bold text-emerald-400">
                    {formatTenge(calculateTotal())}
                  </span>
                </div>
              </div>

              {/* Footer Buttons */}
              <div className="pt-2 flex flex-col sm:flex-row justify-end gap-3 border-t border-[#243045]">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl bg-[#0B0F17] hover:bg-slate-800 text-slate-300 transition text-xs font-semibold"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={
                    isSubmitting ||
                    isBelowMinOrder ||
                    orderItems.length === 0 ||
                    supplierCatalog.length === 0
                  }
                  title={
                    isBelowMinOrder
                      ? `Минимальный заказ ${formatTenge(minOrderAmount)}. Добавьте еще ${formatTenge(missingOrderAmount)}`
                      : ''
                  }
                  className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition disabled:opacity-40 disabled:cursor-not-allowed text-xs shadow-lg shadow-emerald-500/20"
                >
                  {isSubmitting
                    ? 'Сохранение...'
                    : editingOrder
                    ? 'Сохранить изменения черновика'
                    : 'Создать черновик заказа'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document View Modal */}
      {docModalContent && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
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
