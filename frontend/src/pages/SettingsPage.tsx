import React, { useEffect, useState } from 'react';
import {
  Settings,
  Building2,
  Users,
  ShieldCheck,
  Save,
  Plus,
  Clock,
  UserCheck,
  CheckCircle2,
  Lock,
  Mail,
  Phone,
  MapPin,
  X,
  AlertCircle,
  FileCode,
} from 'lucide-react';
import { OrganizationSettings, User, ActivityLogItem, CreateUserData } from '../types';
import { api } from '../services/api';
import { formatDate } from '../utils/formatters';

interface SettingsPageProps {
  currentUser: User | null;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ currentUser }) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'team' | 'audit'>('profile');
  const [settings, setSettings] = useState<OrganizationSettings | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Profile form
  const [formName, setFormName] = useState('');
  const [formBusinessType, setFormBusinessType] = useState('');
  const [formCurrency, setFormCurrency] = useState('KZT');
  const [formAlertThreshold, setFormAlertThreshold] = useState<number>(5);
  const [formLowStockDays, setFormLowStockDays] = useState<number>(5);
  const [formEmail, setFormEmail] = useState('');
  const [formPhone, setFormPhone] = useState('');
  const [formAddress, setFormAddress] = useState('');

  // Add User Modal
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserRole, setNewUserRole] = useState('manager');
  const [newUserPassword, setNewUserPassword] = useState('Staff123!');
  const [isSubmittingUser, setIsSubmittingUser] = useState(false);

  // Audit filter
  const [auditActionFilter, setAuditActionFilter] = useState('all');

  const loadData = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const [sett, usrList, logs] = await Promise.all([
        api.getOrganizationSettings(),
        api.getUsers(),
        api.getActivityLogs({
          action: auditActionFilter !== 'all' ? auditActionFilter : undefined,
        }),
      ]);
      setSettings(sett);
      setUsers(usrList);
      setActivityLogs(logs);

      // Populate form
      setFormName(sett.name);
      setFormBusinessType(sett.business_type);
      setFormCurrency(sett.currency || 'KZT');
      setFormAlertThreshold(sett.price_alert_threshold_percent || 5);
      setFormLowStockDays(sett.low_stock_days_threshold || 5);
      setFormEmail(sett.contact_email || '');
      setFormPhone(sett.contact_phone || '');
      setFormAddress(sett.address || '');
    } catch (err: any) {
      console.error(err);
      setErrorMessage('Ошибка при загрузке настроек');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [auditActionFilter]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      const updated = await api.updateOrganizationSettings({
        name: formName,
        business_type: formBusinessType,
        currency: formCurrency,
        price_alert_threshold_percent: Number(formAlertThreshold),
        low_stock_days_threshold: Number(formLowStockDays),
        contact_email: formEmail || undefined,
        contact_phone: formPhone || undefined,
        address: formAddress || undefined,
      });
      setSettings(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка сохранения настроек');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingUser(true);
    try {
      const payload: CreateUserData = {
        name: newUserName,
        email: newUserEmail,
        role: newUserRole,
        password: newUserPassword,
      };
      await api.createUser(payload);
      setIsAddUserModalOpen(false);
      setNewUserName('');
      setNewUserEmail('');
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка добавления пользователя');
    } finally {
      setIsSubmittingUser(false);
    }
  };

  const getRoleBadge = (role: string) => {
    const r = role.toLowerCase();
    if (r.includes('owner') || r.includes('владелец')) {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
          Владелец (Owner)
        </span>
      );
    }
    if (r.includes('manager') || r.includes('управляющ')) {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">
          Управляющий (Manager)
        </span>
      );
    }
    return (
      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
        Сотрудник (Employee)
      </span>
    );
  };

  const isOwner =
    currentUser?.role?.toLowerCase().includes('owner') ||
    currentUser?.role?.toLowerCase().includes('владелец');

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-emerald-400" />
            Настройки и администрирование
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Конфигурация параметров учета, управление командой и системный аудит действий
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs">
          {errorMessage}
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-[#243045] gap-4">
        <button
          onClick={() => setActiveTab('profile')}
          className={`pb-3 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'profile'
              ? 'border-emerald-500 text-white'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Building2 className="w-4 h-4" />
          <span>Профиль предприятия</span>
        </button>
        <button
          onClick={() => setActiveTab('team')}
          className={`pb-3 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'team'
              ? 'border-emerald-500 text-white'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Команда и роли ({users.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`pb-3 text-xs font-bold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'audit'
              ? 'border-emerald-500 text-white'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Журнал аудита ({activityLogs.length})</span>
        </button>
      </div>

      {/* Tab 1: Profile Settings */}
      {activeTab === 'profile' && (
        <div className="max-w-3xl rounded-2xl bg-[#161F30] border border-[#243045] p-5 sm:p-7">
          <form onSubmit={handleSaveProfile} className="space-y-5 text-xs">
            <div className="border-b border-[#243045] pb-4">
              <h3 className="text-sm font-bold text-white mb-1">Основные реквизиты</h3>
              <p className="text-slate-400 text-[11px]">
                Информация об организации используется в печатных формах накладных и отчетах
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-400 mb-1">Название предприятия *</label>
                <input
                  type="text"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Тип деятельности *</label>
                <input
                  type="text"
                  value={formBusinessType}
                  onChange={(e) => setFormBusinessType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Валюта учета</label>
                <select
                  value={formCurrency}
                  onChange={(e) => setFormCurrency(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="KZT">KZT — Казахстанский тенге (₸)</option>
                  <option value="RUB">RUB — Российский рубль (₽)</option>
                  <option value="USD">USD — Доллар США ($)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Порог алерта о росте цен (%)</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={formAlertThreshold}
                  onChange={(e) => setFormAlertThreshold(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            <div className="border-t border-[#243045] pt-4">
              <h3 className="text-sm font-bold text-white mb-3">Контакты и адрес</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 mb-1 flex items-center gap-1">
                    <Mail className="w-3 h-3" /> Контактный E-mail
                  </label>
                  <input
                    type="email"
                    value={formEmail}
                    onChange={(e) => setFormEmail(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 flex items-center gap-1">
                    <Phone className="w-3 h-3" /> Контактный телефон
                  </label>
                  <input
                    type="text"
                    value={formPhone}
                    onChange={(e) => setFormPhone(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-slate-400 mb-1 flex items-center gap-1">
                    <MapPin className="w-3 h-3" /> Фактический адрес кофейни
                  </label>
                  <input
                    type="text"
                    value={formAddress}
                    onChange={(e) => setFormAddress(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>

            <div className="pt-3 flex items-center justify-between border-t border-[#243045]">
              {saveSuccess && (
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Настройки успешно сохранены!
                </span>
              )}
              <div className="ml-auto">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition shadow-lg shadow-emerald-500/20"
                >
                  <Save className="w-4 h-4" />
                  <span>{isSaving ? 'Сохранение...' : 'Сохранить изменения'}</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* Tab 2: Team & Roles */}
      {activeTab === 'team' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Пользователи организации</h3>
              <p className="text-xs text-slate-400">
                Ролевая модель доступа: Owner (полный доступ), Manager (управление заказами и складом), Employee (просмотр и списания)
              </p>
            </div>
            {isOwner && (
              <button
                onClick={() => setIsAddUserModalOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition shadow-md"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Добавить сотрудника</span>
              </button>
            )}
          </div>

          <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase bg-[#0F172A]/50">
                  <th className="py-3 px-4">Сотрудник</th>
                  <th className="py-3 px-4">E-mail логин</th>
                  <th className="py-3 px-4">Роль в системе</th>
                  <th className="py-3 px-4 text-center">Статус</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243045]/60 text-slate-300">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-4 font-semibold text-white flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-emerald-400 font-bold">
                        {u.name.charAt(0)}
                      </div>
                      <span>{u.name}</span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400 text-[11px]">{u.email}</td>
                    <td className="py-3 px-4">{getRoleBadge(u.role)}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                        Активен
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Security & Activity Audit */}
      {activeTab === 'audit' && (
        <div className="space-y-4">
          <div className="p-3.5 rounded-2xl bg-[#161F30] border border-[#243045] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Фильтр событий:</span>
              <select
                value={auditActionFilter}
                onChange={(e) => setAuditActionFilter(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs focus:outline-none"
              >
                <option value="all">Все события</option>
                <option value="create_order">Создание заказов</option>
                <option value="receive_order">Приемка поставок</option>
                <option value="stock_adjustment">Инвентаризации</option>
                <option value="stock_write_off">Списания</option>
                <option value="import">Импорт данных</option>
                <option value="update_settings">Изменение настроек</option>
              </select>
            </div>
            <span className="text-[11px] text-slate-500">
              Неизменяемый журнал безопасности BizMind
            </span>
          </div>

          <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase bg-[#0F172A]/50">
                  <th className="py-3 px-4">Время</th>
                  <th className="py-3 px-4">Пользователь</th>
                  <th className="py-3 px-4">Действие</th>
                  <th className="py-3 px-4">Сущность</th>
                  <th className="py-3 px-4">Детали операции</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#243045]/60 text-slate-300">
                {activityLogs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-500">
                      Нет зарегистрированных событий аудита
                    </td>
                  </tr>
                ) : (
                  activityLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 px-4 whitespace-nowrap text-slate-400 font-mono text-[11px]">
                        {formatDate(log.created_at)}
                      </td>
                      <td className="py-3 px-4 font-medium text-white">{log.user_name}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                          {log.action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                        {log.entity_type} {log.entity_id ? `#${log.entity_id}` : ''}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px] max-w-xs truncate">
                        {log.details ? JSON.stringify(log.details) : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      {isAddUserModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#243045] pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-emerald-400" />
                Добавить сотрудника
              </h3>
              <button
                onClick={() => setIsAddUserModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Имя и фамилия *</label>
                <input
                  type="text"
                  placeholder="Иван Петров"
                  value={newUserName}
                  onChange={(e) => setNewUserName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">E-mail (логин) *</label>
                <input
                  type="email"
                  placeholder="ivan@cafe.kz"
                  value={newUserEmail}
                  onChange={(e) => setNewUserEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Роль *</label>
                <select
                  value={newUserRole}
                  onChange={(e) => setNewUserRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="manager">Manager (Управляющий)</option>
                  <option value="employee">Employee (Бариста / Сотрудник)</option>
                  <option value="owner">Owner (Владелец)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Пароль для входа *</label>
                <input
                  type="password"
                  value={newUserPassword}
                  onChange={(e) => setNewUserPassword(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddUserModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#0B0F17] hover:bg-slate-800 text-slate-300"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingUser}
                  className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold"
                >
                  {isSubmittingUser ? 'Создание...' : 'Зарегистрировать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default SettingsPage;
