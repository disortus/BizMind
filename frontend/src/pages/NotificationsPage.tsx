import React, { useEffect, useState } from 'react';
import {
  Bell,
  CheckCircle,
  AlertTriangle,
  Info,
  TrendingUp,
  Check,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';
import { NotificationItem } from '../types';
import { api } from '../services/api';
import { formatDate } from '../utils/formatters';

interface NotificationsPageProps {
  onNavigate: (tab: string, productId?: number) => void;
  onRefreshUnread: () => void;
}

export const NotificationsPage: React.FC<NotificationsPageProps> = ({
  onNavigate,
  onRefreshUnread,
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const data = await api.getNotifications(unreadOnly);
      setNotifications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [unreadOnly]);

  const handleMarkRead = async (id: number) => {
    try {
      await api.markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      onRefreshUnread();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      onRefreshUnread();
    } catch (err) {
      console.error(err);
    }
  };

  const getActionTarget = (notif: NotificationItem): { tab: string; label: string } => {
    if (notif.notification_type === 'price_spike' || notif.notification_type === 'alternative_offer') {
      return { tab: 'comparison', label: 'Сравнить цены' };
    }
    if (notif.notification_type === 'low_stock') {
      return { tab: 'forecast', label: 'Проверить остатки' };
    }
    return { tab: 'finances', label: 'Открыть финансы' };
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            Центр уведомлений и сигналов
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            События изменения цен, остатков и расходов на основе правил
          </p>
        </div>

        <div className="flex items-center gap-2 sm:gap-3 w-full sm:w-auto">
          <button
            onClick={() => setUnreadOnly(!unreadOnly)}
            className={`flex-1 sm:flex-none justify-center px-3 py-2 sm:py-1.5 rounded-xl text-xs font-medium border transition ${
              unreadOnly
                ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
                : 'bg-[#161F30] border-[#243045] text-slate-400 hover:text-white'
            }`}
          >
            {unreadOnly ? 'Только новые' : 'Все уведомления'}
          </button>

          <button
            onClick={handleMarkAllRead}
            className="flex-1 sm:flex-none justify-center flex items-center gap-1.5 px-3 py-2 sm:py-1.5 rounded-xl bg-[#161F30] border border-[#243045] text-slate-300 hover:text-white text-xs font-medium transition"
          >
            <Check className="w-3.5 h-3.5" />
            <span>Прочитать все</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-16 text-center text-slate-500 text-xs">Загрузка уведомлений...</div>
      ) : notifications.length === 0 ? (
        <div className="p-16 rounded-2xl bg-[#161F30] border border-[#243045] text-center text-slate-400 text-xs">
          Нет активных уведомлений.
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => {
            const action = getActionTarget(n);
            const isDanger = n.severity === 'danger';
            const isWarning = n.severity === 'warning';
            const isSuccess = n.severity === 'success';

            return (
              <div
                key={n.id}
                className={`p-4 sm:p-5 rounded-2xl border transition flex flex-col sm:flex-row sm:items-start justify-between gap-4 ${
                  !n.is_read
                    ? isDanger
                      ? 'bg-rose-950/20 border-rose-500/30'
                      : isSuccess
                      ? 'bg-emerald-950/20 border-emerald-500/30'
                      : isWarning
                      ? 'bg-amber-950/20 border-amber-500/30'
                      : 'bg-[#161F30] border-[#334155]'
                    : 'bg-[#161F30]/60 border-[#243045] opacity-75'
                }`}
              >
                <div className="flex items-start gap-3.5">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                      isDanger
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : isSuccess
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : isWarning
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {isDanger && <ShieldAlert className="w-5 h-5" />}
                    {isSuccess && <TrendingUp className="w-5 h-5" />}
                    {isWarning && <AlertTriangle className="w-5 h-5" />}
                    {n.severity === 'info' && <Info className="w-5 h-5" />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-bold text-white">{n.title}</h4>
                      {!n.is_read && (
                        <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {n.description}
                    </p>
                    <div className="text-[10px] text-slate-500 mt-2 font-mono">
                      {formatDate(n.created_at)}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-2 shrink-0 pt-3 sm:pt-0 border-t border-[#243045]/60 sm:border-t-0 w-full sm:w-auto">
                  <button
                    onClick={() => {
                      if (!n.is_read) handleMarkRead(n.id);
                      onNavigate(action.tab, n.related_product_id || undefined);
                    }}
                    className="flex-1 sm:flex-none justify-center px-3 py-2 sm:py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1 shadow-sm transition"
                  >
                    <span>{action.label}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  {!n.is_read && (
                    <button
                      onClick={() => handleMarkRead(n.id)}
                      className="p-2 sm:p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                      title="Пометить как прочитанное"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
