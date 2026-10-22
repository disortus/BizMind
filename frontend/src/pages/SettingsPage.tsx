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
  RotateCcw,
} from 'lucide-react';
import { OrganizationSettings, User, ActivityLogItem, CreateUserData } from '../types';
import { api } from '../services/api';
import { formatDate } from '../utils/formatters';
import { formatApiError } from '../utils/error';

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
  const [saveError, setSaveError] = useState<string | null>(null);

  // Profile form
  const [formName, setFormName] = useState('');
  const [formBusinessType, setFormBusinessType] = useState('');
  const [formCurrency, setFormCurrency] = useState('KZT');
  const [formAlertThreshold, setFormAlertThreshold] = useState<number>(5);
  const [formLowStockDays, setFormLowStockDays] = useState<number>(5);
  const [formEmail, setFormEmail] = useState('');
  const [formPhone, setFormPhone] = useState('');
  const [formAddress, setFormAddress] = useState('');
  const [profileErrors, setProfileErrors] = useState<Record<string, string>>({});

  // Add User Modal
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserRole, setNewUserRole] = useState('manager');
  const [newUserPassword, setNewUserPassword] = useState('Staff123!');
  const [isSubmittingUser, setIsSubmittingUser] = useState(false);
  const [userFormErrors, setUserFormErrors] = useState<Record<string, string>>({});
  const [userSubmitError, setUserSubmitError] = useState<string | null>(null);

  // Audit filter
  const [auditActionFilter, setAuditActionFilter] = useState('all');

  const loadData = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const results = await Promise.allSettled([
        api.getOrganizationSettings(),
        api.getUsers(),
        api.getActivityLogs({
          action: auditActionFilter !== 'all' ? auditActionFilter : undefined,
        }),
      ]);

      const [settRes, usrRes, logsRes] = results;

      if (settRes.status === 'fulfilled') {
        const sett = settRes.value;
        setSettings(sett);
        // Populate form
        setFormName(sett.name || '');
        setFormBusinessType(sett.business_type || '');
        setFormCurrency(sett.currency || 'KZT');
        setFormAlertThreshold(sett.price_alert_threshold_percent ?? sett.alert_threshold_percent ?? 5);
        setFormLowStockDays(sett.low_stock_days_threshold || 5);
        setFormEmail(sett.contact_email || sett.email || '');
        setFormPhone(sett.contact_phone || sett.phone || '');
        setFormAddress(sett.address || '');
      } else {
        console.warn('Failed to load settings:', settRes.reason);
      }

      if (usrRes.status === 'fulfilled') {
        setUsers(usrRes.value || []);
      } else {
        console.warn('Failed to load users:', usrRes.reason);
      }

      if (logsRes.status === 'fulfilled') {
        setActivityLogs(logsRes.value || []);
      } else {
        console.warn('Failed to load activity logs:', logsRes.reason);
      }

      if (settRes.status === 'rejected' && usrRes.status === 'rejected' && logsRes.status === 'rejected') {
        setErrorMessage(formatApiError(settRes.reason, 'Ошибка при загрузке настроек'));
      }
    } catch (err: any) {
      console.error(err);
      setErrorMessage(formatApiError(err, 'Ошибка при загрузке настроек'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [auditActionFilter]);

  const validateProfileForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!formName.trim() || formName.trim().length < 2) {
      errors.name = 'Название предприятия должно содержать не менее 2 символов';
    }
    if (!formBusinessType.trim() || formBusinessType.trim().length < 2) {
      errors.business_type = 'Укажите тип деятельности предприятия';
    }
    if (isNaN(formAlertThreshold) || formAlertThreshold < 1 || formAlertThreshold > 100) {
      errors.alert_threshold = 'Порог оповещения должен быть в диапазоне от 1% до 100%';
    }
    if (isNaN(formLowStockDays) || formLowStockDays < 1 || formLowStockDays > 90) {
      errors.low_stock = 'Порог неснижаемого остатка должен быть от 1 до 90 дней';
    }
    if (formEmail.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formEmail.trim())) {
      errors.email = 'Укажите корректный адрес электронной почты (например, info@cafe.kz)';
    }
    if (formPhone.trim() && formPhone.replace(/\D/g, '').length < 6) {
      errors.phone = 'Укажите корректный контактный номер телефона';
    }

    setProfileErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateProfileForm()) {
      return;
    }

    setIsSaving(true);
    setSaveSuccess(false);
    setSaveError(null);
    try {
      const updated = await api.updateOrganizationSettings({
        name: formName.trim(),
        business_type: formBusinessType.trim(),
        currency: formCurrency,
        price_alert_threshold_percent: Number(formAlertThreshold),
        low_stock_days_threshold: Number(formLowStockDays),
        contact_email: formEmail.trim() || undefined,
        contact_phone: formPhone.trim() || undefined,
        address: formAddress.trim() || undefined,
      });
      setSettings(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
      await loadData();
    } catch (err: any) {
      setSaveError(formatApiError(err, 'Ошибка сохранения настроек'));
    } finally {
      setIsSaving(false);
    }
  };

  const validateUserForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!newUserName.trim() || newUserName.trim().length < 2) {
      errors.name = 'Имя и фамилия сотрудника должны быть не короче 2 символов';
    }
    if (!newUserEmail.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newUserEmail.trim())) {
      errors.email = 'Укажите действительный адрес электронной почты (например: user@cafe.kz)';
    }
    if (!newUserPassword || newUserPassword.length < 6) {
      errors.password = 'Пароль должен содержать минимум 6 символов';
    }
    if (!['owner', 'manager', 'employee'].includes(newUserRole.toLowerCase())) {
      errors.role = 'Выберите корректную роль сотрудника';
    }

    setUserFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateUserForm()) {
      return;
    }

    setIsSubmittingUser(true);
    setUserSubmitError(null);
    try {
      const payload: CreateUserData = {
        name: newUserName.trim(),
        email: newUserEmail.trim().toLowerCase(),
        role: newUserRole,
        password: newUserPassword,
      };
      await api.createUser(payload);
      setIsAddUserModalOpen(false);
      setNewUserName('');
      setNewUserEmail('');
      setUserFormErrors({});
      await loadData();
    } catch (err: any) {
      setUserSubmitError(formatApiError(err, 'Ошибка добавления сотрудника'));
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
    !currentUser?.role ||
    currentUser.role.toLowerCase().includes('owner') ||
    currentUser.role.toLowerCase().includes('владелец') ||
    currentUser.role.toLowerCase().includes('управляющ');

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
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#161F30] hover:bg-[#1E293B] border border-[#243045] text-slate-300 text-xs font-semibold transition"
          title="Обновить данные"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Обновить</span>
        </button>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
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
                Информация об организации используется в печатных формах накладных, заказах и отчетах
              </p>
            </div>

            {saveError && (
              <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{saveError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-400 mb-1">
                  Название предприятия <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  value={formName}
                  onChange={(e) => {
                    setFormName(e.target.value);
                    if (profileErrors.name) setProfileErrors((prev) => ({ ...prev, name: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border text-white focus:outline-none ${
                    profileErrors.name ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                  }`}
                  placeholder="Cafe Aroma"
                  required
                />
                {profileErrors.name && (
                  <p className="text-[11px] text-rose-400 mt-1">{profileErrors.name}</p>
                )}
              </div>

              <div>
                <label className="block text-slate-400 mb-1">
                  Тип деятельности <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  value={formBusinessType}
                  onChange={(e) => {
                    setFormBusinessType(e.target.value);
                    if (profileErrors.business_type) setProfileErrors((prev) => ({ ...prev, business_type: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border text-white focus:outline-none ${
                    profileErrors.business_type ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                  }`}
                  placeholder="Кофейня / Общепит"
                  required
                />
                {profileErrors.business_type && (
                  <p className="text-[11px] text-rose-400 mt-1">{profileErrors.business_type}</p>
                )}
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
                <label className="block text-slate-400 mb-1">
                  Порог алерта о росте цен (%) <span className="text-rose-400">*</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={formAlertThreshold}
                  onChange={(e) => {
                    setFormAlertThreshold(Number(e.target.value));
                    if (profileErrors.alert_threshold) setProfileErrors((prev) => ({ ...prev, alert_threshold: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border font-mono text-white focus:outline-none ${
                    profileErrors.alert_threshold ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                  }`}
                />
                {profileErrors.alert_threshold ? (
                  <p className="text-[11px] text-rose-400 mt-1">{profileErrors.alert_threshold}</p>
                ) : (
                  <p className="text-[10px] text-slate-500 mt-0.5">Уведомлять при скачке закупочной цены выше этого %</p>
                )}
              </div>

              <div>
                <label className="block text-slate-400 mb-1">
                  Порог неснижаемого остатка (дни)
                </label>
                <input
                  type="number"
                  min="1"
                  max="90"
                  value={formLowStockDays}
                  onChange={(e) => {
                    setFormLowStockDays(Number(e.target.value));
                    if (profileErrors.low_stock) setProfileErrors((prev) => ({ ...prev, low_stock: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border font-mono text-white focus:outline-none ${
                    profileErrors.low_stock ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                  }`}
                />
                {profileErrors.low_stock ? (
                  <p className="text-[11px] text-rose-400 mt-1">{profileErrors.low_stock}</p>
                ) : (
                  <p className="text-[10px] text-slate-500 mt-0.5">Порог дней автономности для предупреждения о дефиците</p>
                )}
              </div>
            </div>

            <div className="border-t border-[#243045] pt-4">
              <h3 className="text-sm font-bold text-white mb-3">Контакты и адрес</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-400 mb-1 flex items-center gap-1">
                    <Mail className="w-3 h-3 text-emerald-400" /> Контактный E-mail
                  </label>
                  <input
                    type="email"
                    value={formEmail}
                    onChange={(e) => {
                      setFormEmail(e.target.value);
                      if (profileErrors.email) setProfileErrors((prev) => ({ ...prev, email: '' }));
                    }}
                    placeholder="contact@cafe.kz"
                    className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border text-white focus:outline-none ${
                      profileErrors.email ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                    }`}
                  />
                  {profileErrors.email && (
                    <p className="text-[11px] text-rose-400 mt-1">{profileErrors.email}</p>
                  )}
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 flex items-center gap-1">
                    <Phone className="w-3 h-3 text-emerald-400" /> Контактный телефон
                  </label>
                  <input
                    type="text"
                    value={formPhone}
                    onChange={(e) => {
                      setFormPhone(e.target.value);
                      if (profileErrors.phone) setProfileErrors((prev) => ({ ...prev, phone: '' }));
                    }}
                    placeholder="+7 (777) 123-45-67"
                    className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border text-white focus:outline-none ${
                      profileErrors.phone ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                    }`}
                  />
                  {profileErrors.phone && (
                    <p className="text-[11px] text-rose-400 mt-1">{profileErrors.phone}</p>
                  )}
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-slate-400 mb-1 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-emerald-400" /> Фактический адрес заведения
                  </label>
                  <input
                    type="text"
                    value={formAddress}
                    onChange={(e) => setFormAddress(e.target.value)}
                    placeholder="г. Алматы, пр. Достык, 42"
                    className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>

            <div className="pt-3 flex items-center justify-between border-t border-[#243045]">
              {saveSuccess && (
                <span className="text-emerald-400 font-semibold flex items-center gap-1.5 animate-fadeIn">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Настройки успешно сохранены!
                </span>
              )}
              <div className="ml-auto">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition shadow-lg shadow-emerald-500/20 disabled:opacity-50"
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
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-white">Пользователи организации</h3>
              <p className="text-xs text-slate-400">
                Ролевая модель доступа: Owner (полный доступ), Manager (управление заказами и складом), Employee (просмотр и списания)
              </p>
            </div>
            {isOwner && (
              <button
                onClick={() => {
                  setUserSubmitError(null);
                  setUserFormErrors({});
                  setIsAddUserModalOpen(true);
                }}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition shadow-md self-start sm:self-auto"
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
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-slate-500">
                      Сотрудники не найдены. Вы можете добавить первого сотрудника с помощью кнопки выше.
                    </td>
                  </tr>
                ) : (
                  users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 px-4 font-semibold text-white flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-emerald-400 font-bold">
                          {u.name ? u.name.charAt(0).toUpperCase() : 'U'}
                        </div>
                        <span>{u.name}</span>
                        {currentUser?.id === u.id && (
                          <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/30">
                            Вы
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-400 text-[11px]">{u.email}</td>
                      <td className="py-3 px-4">{getRoleBadge(u.role)}</td>
                      <td className="py-3 px-4 text-center">
                        <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                          Активен
                        </span>
                      </td>
                    </tr>
                  ))
                )}
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
                <option value="all">Все события ({activityLogs.length})</option>
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
                      Нет зарегистрированных событий аудита для выбранного фильтра
                    </td>
                  </tr>
                ) : (
                  activityLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 px-4 whitespace-nowrap text-slate-400 font-mono text-[11px]">
                        {formatDate(log.created_at)}
                      </td>
                      <td className="py-3 px-4 font-medium text-white">{log.user_name || 'Система'}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                          {log.action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                        {log.entity_type} {log.entity_id ? `#${log.entity_id}` : ''}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px] max-w-xs truncate">
                        {log.details ? (typeof log.details === 'string' ? log.details : JSON.stringify(log.details)) : '—'}
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
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl animate-scaleIn">
            <div className="flex items-center justify-between border-b border-[#243045] pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-emerald-400" />
                Добавить сотрудника в команду
              </h3>
              <button
                onClick={() => setIsAddUserModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {userSubmitError && (
              <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{userSubmitError}</span>
              </div>
            )}

            <form onSubmit={handleCreateUser} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">
                  Имя и фамилия <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="Иван Петров"
                  value={newUserName}
                  onChange={(e) => {
                    setNewUserName(e.target.value);
                    if (userFormErrors.name) setUserFormErrors((prev) => ({ ...prev, name: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border text-white focus:outline-none ${
                    userFormErrors.name ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                  }`}
                  required
                />
                {userFormErrors.name && (
                  <p className="text-[11px] text-rose-400 mt-1">{userFormErrors.name}</p>
                )}
              </div>

              <div>
                <label className="block text-slate-400 mb-1">
                  E-mail (логин входа) <span className="text-rose-400">*</span>
                </label>
                <input
                  type="email"
                  placeholder="ivan@cafe.kz"
                  value={newUserEmail}
                  onChange={(e) => {
                    setNewUserEmail(e.target.value);
                    if (userFormErrors.email) setUserFormErrors((prev) => ({ ...prev, email: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border text-white focus:outline-none ${
                    userFormErrors.email ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                  }`}
                  required
                />
                {userFormErrors.email && (
                  <p className="text-[11px] text-rose-400 mt-1">{userFormErrors.email}</p>
                )}
              </div>

              <div>
                <label className="block text-slate-400 mb-1">
                  Роль в системе <span className="text-rose-400">*</span>
                </label>
                <select
                  value={newUserRole}
                  onChange={(e) => setNewUserRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="manager">Manager (Управляющий — заказы, склад, закупки)</option>
                  <option value="employee">Employee (Бариста / Сотрудник — просмотр и списания)</option>
                  <option value="owner">Owner (Владелец — полный доступ и администрирование)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">
                  Пароль для входа <span className="text-rose-400">*</span>
                </label>
                <input
                  type="password"
                  value={newUserPassword}
                  onChange={(e) => {
                    setNewUserPassword(e.target.value);
                    if (userFormErrors.password) setUserFormErrors((prev) => ({ ...prev, password: '' }));
                  }}
                  placeholder="Не менее 6 символов"
                  className={`w-full px-3 py-2 rounded-xl bg-[#0B0F17] border text-white focus:outline-none ${
                    userFormErrors.password ? 'border-rose-500 focus:border-rose-400' : 'border-[#243045] focus:border-emerald-500'
                  }`}
                  required
                />
                {userFormErrors.password && (
                  <p className="text-[11px] text-rose-400 mt-1">{userFormErrors.password}</p>
                )}
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-[#243045]">
                <button
                  type="button"
                  onClick={() => setIsAddUserModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#0B0F17] hover:bg-slate-800 text-slate-300 font-semibold"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingUser}
                  className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold disabled:opacity-50 transition"
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
