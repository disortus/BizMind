import React, { useEffect, useState } from 'react';
import {
  FileText,
  Plus,
  Copy,
  Trash2,
  Edit3,
  Download,
  FileSpreadsheet,
  SlidersHorizontal,
  DollarSign,
  Package,
  ShoppingBag,
  Building,
  Check,
  X,
  BarChart3,
} from 'lucide-react';
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area,
} from 'recharts';
import {
  ReportTemplate,
  ReportTemplateConfig,
  ReportPreviewResponse,
} from '../types';
import { api } from '../services/api';
import { formatTenge } from '../utils/formatters';

interface ReportBuilderPageProps {
  onNavigateToImport?: () => void;
}

const REPORT_TYPE_LABELS: Record<string, { label: string; icon: any; color: string }> = {
  financial: { label: 'Финансовый отчёт', icon: DollarSign, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  procurement: { label: 'Анализ закупок и цен', icon: ShoppingBag, color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  inventory: { label: 'Склад и запасы', icon: Package, color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  executive: { label: 'Сводный отчёт владельца', icon: BarChart3, color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
};

const PERIOD_LABELS: Record<string, string> = {
  current_month: 'Текущий месяц',
  previous_month: 'Предыдущий месяц',
  last_30d: 'Последние 30 дней',
  last_90d: 'Последние 90 дней',
  custom: 'Пользовательский период',
};

const GROUP_BY_LABELS: Record<string, string> = {
  category: 'По категориям',
  supplier: 'По поставщикам',
  month: 'По месяцам',
  day: 'По дням',
};

export const ReportBuilderPage: React.FC<ReportBuilderPageProps> = ({ onNavigateToImport }) => {
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'all' | 'system' | 'custom'>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null);

  // Preview state
  const [previewData, setPreviewData] = useState<ReportPreviewResponse | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewConfig, setPreviewConfig] = useState<ReportTemplateConfig | null>(null);

  // Edit / Create Modal state
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<ReportTemplate | null>(null);
  const [formTitle, setFormTitle] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formReportType, setFormReportType] = useState<'financial' | 'procurement' | 'inventory' | 'executive'>('financial');
  const [formPeriod, setFormPeriod] = useState<string>('last_90d');
  const [formGroupBy, setFormGroupBy] = useState<string>('category');
  const [formSortBy, setFormSortBy] = useState<string>('amount_desc');
  const [formSections, setFormSections] = useState<string[]>(['kpi_summary', 'detailed_table']);
  const [formStartDate, setFormStartDate] = useState('');
  const [formEndDate, setFormEndDate] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Export states
  const [exportingExcel, setExportingExcel] = useState(false);
  const [exportingCsv, setExportingCsv] = useState(false);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await api.getReportTemplates();
      setTemplates(data);
      if (data.length > 0 && !selectedTemplate) {
        handleSelectTemplateForPreview(data[0]);
      }
    } catch (err) {
      console.error('Failed to load templates:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleSelectTemplateForPreview = async (template: ReportTemplate) => {
    setSelectedTemplate(template);
    const cfg = { ...template.config, title: template.title };
    setPreviewConfig(cfg);
    await runPreview(template.report_type, cfg);
  };

  const runPreview = async (reportType: string, config: ReportTemplateConfig) => {
    try {
      setPreviewLoading(true);
      const res = await api.previewReport({
        report_type: reportType,
        config: config,
      });
      setPreviewData(res);
    } catch (err) {
      console.error('Preview error:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setEditingTemplate(null);
    setFormTitle('Новый аналитический отчёт');
    setFormDesc('');
    setFormReportType('financial');
    setFormPeriod('current_month');
    setFormGroupBy('category');
    setFormSortBy('amount_desc');
    setFormSections(['kpi_summary', 'detailed_table']);
    setFormStartDate('');
    setFormEndDate('');
    setSaveError(null);
    setIsEditorOpen(true);
  };

  const handleOpenEdit = (t: ReportTemplate) => {
    if (t.is_system) return;
    setEditingTemplate(t);
    setFormTitle(t.title);
    setFormDesc(t.description || '');
    setFormReportType(t.report_type);
    setFormPeriod(t.config.period_type || 'current_month');
    setFormGroupBy(t.config.group_by || 'category');
    setFormSortBy(t.config.sort_by || 'amount_desc');
    setFormSections(t.config.sections || ['kpi_summary', 'detailed_table']);
    setFormStartDate(t.config.start_date || '');
    setFormEndDate(t.config.end_date || '');
    setSaveError(null);
    setIsEditorOpen(true);
  };

  const handleSaveTemplate = async () => {
    if (!formTitle.trim()) {
      setSaveError('Пожалуйста, укажите название шаблона');
      return;
    }

    setSaving(true);
    setSaveError(null);
    try {
      const cfg: ReportTemplateConfig = {
        title: formTitle.trim(),
        period_type: formPeriod,
        group_by: formGroupBy,
        sort_by: formSortBy,
        sections: formSections,
        start_date: formPeriod === 'custom' && formStartDate ? formStartDate : undefined,
        end_date: formPeriod === 'custom' && formEndDate ? formEndDate : undefined,
      };

      if (editingTemplate) {
        const updated = await api.updateReportTemplate(editingTemplate.id, {
          title: formTitle.trim(),
          description: formDesc.trim() || undefined,
          report_type: formReportType,
          config: cfg,
        });
        await loadTemplates();
        setIsEditorOpen(false);
        handleSelectTemplateForPreview(updated);
      } else {
        const created = await api.createReportTemplate({
          title: formTitle.trim(),
          description: formDesc.trim() || undefined,
          report_type: formReportType,
          config: cfg,
        });
        await loadTemplates();
        setIsEditorOpen(false);
        handleSelectTemplateForPreview(created);
      }
    } catch (err: any) {
      setSaveError(err.response?.data?.detail || 'Ошибка сохранения шаблона');
    } finally {
      setSaving(false);
    }
  };

  const handleDuplicate = async (t: ReportTemplate) => {
    try {
      setLoading(true);
      const copy = await api.duplicateReportTemplate(t.id);
      await loadTemplates();
      handleSelectTemplateForPreview(copy);
    } catch (err) {
      console.error('Failed to duplicate template:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (t: ReportTemplate) => {
    if (t.is_system) {
      alert('Системные шаблоны BizMind защищены от удаления.');
      return;
    }
    if (!confirm(`Вы действительно хотите удалить шаблон «${t.title}»?`)) {
      return;
    }
    try {
      await api.deleteReportTemplate(t.id);
      await loadTemplates();
      if (selectedTemplate?.id === t.id) {
        setSelectedTemplate(null);
        setPreviewData(null);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка удаления шаблона');
    }
  };

  const handleExportExcel = async () => {
    if (!selectedTemplate || !previewConfig) return;
    try {
      setExportingExcel(true);
      const blob = await api.exportReportExcel({
        report_type: selectedTemplate.report_type,
        config: previewConfig,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${selectedTemplate.report_type}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Excel export failed:', err);
      alert('Не удалось выгрузить Excel-файл');
    } finally {
      setExportingExcel(false);
    }
  };

  const handleExportCsv = async () => {
    if (!selectedTemplate || !previewConfig) return;
    try {
      setExportingCsv(true);
      const blob = await api.exportReportCsv({
        report_type: selectedTemplate.report_type,
        config: previewConfig,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${selectedTemplate.report_type}_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('CSV export failed:', err);
      alert('Не удалось выгрузить CSV-файл');
    } finally {
      setExportingCsv(false);
    }
  };

  const filteredTemplates = templates.filter((t) => {
    if (activeTab === 'system') return t.is_system;
    if (activeTab === 'custom') return !t.is_system;
    return true;
  });

  const toggleSection = (sec: string) => {
    if (formSections.includes(sec)) {
      if (formSections.length > 1) {
        setFormSections(formSections.filter((s) => s !== sec));
      }
    } else {
      setFormSections([...formSections, sec]);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* 1. Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20">
              Новая функциональность BizMind
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <FileText className="w-6 h-6 text-purple-400" />
            Конструктор и шаблонизатор отчётов
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Настраиваемая генерация управленческих отчетов, интерактивный аудит и выгрузка в Microsoft Excel / CSV
          </p>
        </div>

        <button
          onClick={handleOpenCreate}
          className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>Создать шаблон</span>
        </button>
      </div>

      {/* 2. Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Templates Library */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#161F30] border border-[#243045]">
            <button
              onClick={() => setActiveTab('all')}
              className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'all'
                  ? 'bg-purple-600 text-white shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Все ({templates.length})
            </button>
            <button
              onClick={() => setActiveTab('system')}
              className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'system'
                  ? 'bg-purple-600 text-white shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Системные ({templates.filter((t) => t.is_system).length})
            </button>
            <button
              onClick={() => setActiveTab('custom')}
              className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'custom'
                  ? 'bg-purple-600 text-white shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Мои ({templates.filter((t) => !t.is_system).length})
            </button>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">
                Загрузка библиотеки шаблонов...
              </div>
            ) : filteredTemplates.length === 0 ? (
              <div className="p-8 rounded-2xl bg-[#161F30] border border-[#243045] text-center text-slate-400 text-xs">
                В этой категории нет шаблонов. Создайте собственный шаблон или скопируйте системный пресет.
              </div>
            ) : (
              filteredTemplates.map((t) => {
                const meta = REPORT_TYPE_LABELS[t.report_type] || REPORT_TYPE_LABELS.financial;
                const Icon = meta.icon;
                const isSelected = selectedTemplate?.id === t.id;

                return (
                  <div
                    key={t.id}
                    onClick={() => handleSelectTemplateForPreview(t)}
                    className={`p-4 rounded-2xl border transition cursor-pointer relative group ${
                      isSelected
                        ? 'bg-[#1C2638] border-purple-500 shadow-md shadow-purple-500/10'
                        : 'bg-[#161F30] border-[#243045] hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3">
                        <div className={`p-2.5 rounded-xl border ${meta.color}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-bold text-white group-hover:text-purple-300 transition">
                              {t.title}
                            </h4>
                          </div>
                          <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                            {t.description || 'Универсальный аналитический отчет'}
                          </p>
                        </div>
                      </div>

                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider shrink-0 border ${
                          t.is_system
                            ? 'bg-blue-500/10 text-blue-300 border-blue-500/20'
                            : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                        }`}
                      >
                        {t.is_system ? 'Системный' : 'Свой'}
                      </span>
                    </div>

                    <div className="mt-3 pt-3 border-t border-[#243045]/60 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono">
                          {t.config?.period_type && PERIOD_LABELS[t.config.period_type] ? PERIOD_LABELS[t.config.period_type] : 'За период'}
                        </span>
                        <span className="text-slate-500">•</span>
                        <span>{t.config?.group_by && GROUP_BY_LABELS[t.config.group_by] ? GROUP_BY_LABELS[t.config.group_by] : 'По категориям'}</span>
                      </div>

                      <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => handleDuplicate(t)}
                          title="Создать копию"
                          className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition"
                        >
                          <Copy className="w-3.5 h-3.5" />
                        </button>
                        {!t.is_system && (
                          <>
                            <button
                              onClick={() => handleOpenEdit(t)}
                              title="Редактировать"
                              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-purple-400 border border-slate-800 transition"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDelete(t)}
                              title="Удалить"
                              className="p-1.5 rounded-lg bg-slate-900 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 border border-slate-800 transition"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Preview & Exports */}
        <div className="lg:col-span-7 space-y-4">
          <div className="p-4 sm:p-6 rounded-2xl bg-[#161F30] border border-[#243045] space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#243045]">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400">
                  Предпросмотр отчёта в реальном времени
                </span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {selectedTemplate?.title || 'Выберите шаблон отчёта'}
                </h3>
                {previewData && (
                  <p className="text-xs text-slate-400 mt-0.5">
                    Организация: <strong className="text-slate-200">{previewData.organization_name}</strong> • Период: <span className="text-emerald-400">{previewData.period_label}</span>
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleExportExcel}
                  disabled={exportingExcel || !selectedTemplate || previewData?.is_empty}
                  className="px-3 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5 transition disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
                  <span>{exportingExcel ? 'Выгрузка...' : 'Excel (.xlsx)'}</span>
                </button>

                <button
                  onClick={handleExportCsv}
                  disabled={exportingCsv || !selectedTemplate || previewData?.is_empty}
                  className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs font-bold flex items-center gap-1.5 transition disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Download className="w-4 h-4 text-slate-400" />
                  <span>{exportingCsv ? 'Выгрузка...' : 'CSV'}</span>
                </button>
              </div>
            </div>

            {selectedTemplate && previewConfig && (
              <div className="p-3 rounded-xl bg-[#0B0F17] border border-[#243045] flex flex-wrap items-center gap-3 text-xs">
                <div className="flex items-center gap-2 text-slate-400">
                  <SlidersHorizontal className="w-3.5 h-3.5 text-purple-400" />
                  <span className="font-semibold text-slate-300">Период:</span>
                </div>
                <select
                  value={previewConfig.period_type}
                  onChange={(e) => {
                    const next = { ...previewConfig, period_type: e.target.value };
                    setPreviewConfig(next);
                    runPreview(selectedTemplate.report_type, next);
                  }}
                  className="px-2.5 py-1 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs font-semibold focus:outline-none focus:border-purple-500"
                >
                  <option value="current_month">Текущий месяц</option>
                  <option value="previous_month">Предыдущий месяц</option>
                  <option value="last_30d">Последние 30 дней</option>
                  <option value="last_90d">Последние 90 дней</option>
                </select>

                <div className="flex items-center gap-2 text-slate-400 ml-auto">
                  <span className="font-semibold text-slate-300">Группировка:</span>
                  <select
                    value={previewConfig.group_by || 'category'}
                    onChange={(e) => {
                      const next = { ...previewConfig, group_by: e.target.value };
                      setPreviewConfig(next);
                      runPreview(selectedTemplate.report_type, next);
                    }}
                    className="px-2.5 py-1 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs font-semibold focus:outline-none focus:border-purple-500"
                  >
                    <option value="category">По категориям</option>
                    <option value="supplier">По поставщикам</option>
                    <option value="month">По месяцам</option>
                    <option value="day">По дням</option>
                  </select>
                </div>
              </div>
            )}

            {previewLoading ? (
              <div className="p-16 flex flex-col items-center justify-center gap-3 text-center">
                <div className="w-8 h-8 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin"></div>
                <p className="text-xs text-slate-400">Формирование предпросмотра отчёта...</p>
              </div>
            ) : !previewData ? (
              <div className="p-16 text-center text-slate-400 text-xs">
                Выберите шаблон слева для интерактивного анализа
              </div>
            ) : previewData.is_empty ? (
              <div className="p-8 rounded-2xl bg-[#0B0F17] border border-amber-500/30 text-center space-y-4">
                <div className="w-12 h-12 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Building className="w-6 h-6" />
                </div>
                <div className="max-w-md mx-auto">
                  <h4 className="text-sm font-bold text-white">
                    В кофейне «{previewData.organization_name}» ещё нет импортированных данных
                  </h4>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {previewData.message || 'Для формирования отчета необходимо загрузить первичные финансовые операции, накладные или складские остатки.'}
                  </p>
                </div>
                {onNavigateToImport && (
                  <button
                    onClick={onNavigateToImport}
                    className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs inline-flex items-center gap-2 transition shadow-lg"
                  >
                    <span>Перейти к пошаговому импорту</span>
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-6">
                {previewData.kpi_cards && previewData.kpi_cards.length > 0 && (
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {previewData.kpi_cards.map((kpi, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-[#0B0F17] border border-[#243045] relative overflow-hidden"
                      >
                        <div className="text-[11px] text-slate-400 truncate">{kpi.title}</div>
                        <div className="text-base sm:text-lg font-bold font-mono text-white mt-1">
                          {kpi.value}
                        </div>
                        <div className="text-[10px] text-slate-500 mt-0.5 truncate">
                          {kpi.subtitle}
                        </div>
                        {kpi.badge && (
                          <span className="absolute top-2 right-2 text-[9px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-300 font-semibold">
                            {kpi.badge}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {previewData.charts?.dynamics && previewData.charts.dynamics.length > 0 && (
                  <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#243045]">
                    <div className="text-xs font-bold text-white mb-3 flex items-center justify-between">
                      <span>Динамика показателей за период</span>
                      <span className="text-[11px] text-slate-500">Доходы vs Расходы (₸)</span>
                    </div>
                    <div className="h-44 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={previewData.charts.dynamics}>
                          <defs>
                            <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.3} />
                              <stop offset="95%" stopColor="#F43F5E" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1F293D" vertical={false} />
                          <XAxis dataKey="date" stroke="#64748B" fontSize={10} tickLine={false} />
                          <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#0F172A',
                              borderColor: '#334155',
                              borderRadius: '8px',
                              fontSize: '11px',
                            }}
                          />
                          <Area type="monotone" dataKey="income" stroke="#10B981" fill="url(#incomeGrad)" name="Доходы" />
                          <Area type="monotone" dataKey="amount" stroke="#F43F5E" fill="url(#expenseGrad)" name="Расходы" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {previewData.columns && previewData.rows && previewData.rows.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-bold text-white">
                        Табличные данные ({previewData.rows.length} строк)
                      </div>
                      <span className="text-[10px] text-slate-500">
                        Точное соответствие выгружаемому файлу Excel/CSV
                      </span>
                    </div>

                    <div className="overflow-x-auto rounded-xl border border-[#243045] bg-[#0B0F17]">
                      <table className="w-full text-left text-xs min-w-[500px]">
                        <thead>
                          <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase tracking-wider bg-slate-900/60">
                            {previewData.columns.map((c) => (
                              <th key={c.key} className="py-2.5 px-3 font-medium">
                                {c.label}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#243045]/60 text-slate-200">
                          {previewData.rows.map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-slate-800/30 transition">
                              {previewData.columns.map((c) => {
                                const val = row[c.key];
                                const isMoney = typeof val === 'number' && (c.key.includes('amount') || c.key.includes('spend') || c.key.includes('income') || c.key.includes('expense') || c.key.includes('valuation') || c.key.includes('profit') || c.key.includes('cost'));
                                const isPercent = c.key.includes('share') || c.key.includes('margin') || c.key.includes('change');

                                return (
                                  <td key={c.key} className="py-2 px-3 font-mono text-[11px]">
                                    {isMoney
                                      ? `${formatTenge(val)}`
                                      : isPercent
                                      ? `${val}%`
                                      : val !== null && val !== undefined
                                      ? String(val)
                                      : '—'}
                                  </td>
                                );
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 3. Create / Edit Template Modal */}
      {isEditorOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-[#161F30] border border-[#243045] rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
            <div className="p-5 border-b border-[#243045] flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white">
                  {editingTemplate ? `Редактирование: ${editingTemplate.title}` : 'Создание нового шаблона отчёта'}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Настройте тип отчета, аналитические разделы, период и способ агрегации
                </p>
              </div>
              <button
                onClick={() => setIsEditorOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-5 overflow-y-auto space-y-4 text-xs">
              {saveError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300">
                  {saveError}
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Название шаблона *</label>
                <input
                  type="text"
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  placeholder="Например: Ежемесячный аудит себестоимости и запасов"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Описание (для чего используется)</label>
                <textarea
                  rows={2}
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                  placeholder="Краткое назначение отчета для управляющего..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-purple-500 resize-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Тип отчёта</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(REPORT_TYPE_LABELS).map(([key, item]) => {
                    const Icon = item.icon;
                    const isSel = formReportType === key;
                    return (
                      <button
                        key={key}
                        type="button"
                        onClick={() => setFormReportType(key as any)}
                        className={`p-3 rounded-xl border text-left flex items-center gap-2.5 transition ${
                          isSel
                            ? 'bg-purple-950/40 border-purple-500 text-white'
                            : 'bg-[#0B0F17] border-[#243045] text-slate-400 hover:text-white'
                        }`}
                      >
                        <Icon className={`w-4 h-4 ${isSel ? 'text-purple-400' : 'text-slate-500'}`} />
                        <span className="font-semibold">{item.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <div className="space-y-1.5">
                  <label className="text-slate-300 font-semibold">Период по умолчанию</label>
                  <select
                    value={formPeriod}
                    onChange={(e) => setFormPeriod(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="current_month">Текущий месяц</option>
                    <option value="previous_month">Предыдущий месяц</option>
                    <option value="last_30d">Последние 30 дней</option>
                    <option value="last_90d">Последние 90 дней</option>
                    <option value="custom">Пользовательский диапазон</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-slate-300 font-semibold">Группировка</label>
                  <select
                    value={formGroupBy}
                    onChange={(e) => setFormGroupBy(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#0B0F17] border border-[#243045] text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="category">По категориям</option>
                    <option value="supplier">По поставщикам</option>
                    <option value="month">По месяцам</option>
                    <option value="day">По дням</option>
                  </select>
                </div>
              </div>

              {formPeriod === 'custom' && (
                <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-[#0B0F17] border border-[#243045]">
                  <div>
                    <label className="text-[11px] text-slate-400">Начало</label>
                    <input
                      type="date"
                      value={formStartDate}
                      onChange={(e) => setFormStartDate(e.target.value)}
                      className="w-full mt-1 px-3 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400">Конец</label>
                    <input
                      type="date"
                      value={formEndDate}
                      onChange={(e) => setFormEndDate(e.target.value)}
                      className="w-full mt-1 px-3 py-1.5 rounded-lg bg-[#161F30] border border-[#243045] text-white text-xs"
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2 pt-2">
                <label className="text-slate-300 font-semibold">Включаемые разделы отчёта</label>
                <div className="space-y-2">
                  {[
                    { id: 'kpi_summary', label: 'Сводные KPI карточки (выручка, расходы, экономия)' },
                    { id: 'detailed_table', label: 'Детализированная таблица показателей' },
                    { id: 'category_breakdown', label: 'Распределение расходов по категориям' },
                    { id: 'price_changes', label: 'Анализ динамики цен поставщиков' },
                    { id: 'low_stock_table', label: 'Контроль критических остатков' },
                  ].map((sec) => (
                    <label
                      key={sec.id}
                      className="flex items-center gap-2.5 p-2 rounded-xl bg-[#0B0F17] border border-[#243045] cursor-pointer hover:border-slate-600 transition"
                    >
                      <input
                        type="checkbox"
                        checked={formSections.includes(sec.id)}
                        onChange={() => toggleSection(sec.id)}
                        className="rounded border-[#243045] text-purple-600 focus:ring-0 w-4 h-4"
                      />
                      <span className="text-slate-300">{sec.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-[#243045] flex items-center justify-end gap-2 bg-[#0F172A]/80">
              <button
                type="button"
                onClick={() => setIsEditorOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition"
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={handleSaveTemplate}
                disabled={saving}
                className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center gap-2 transition disabled:opacity-50 shadow-md"
              >
                {saving ? (
                  <span>Сохранение...</span>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    <span>{editingTemplate ? 'Сохранить изменения' : 'Создать шаблон'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
