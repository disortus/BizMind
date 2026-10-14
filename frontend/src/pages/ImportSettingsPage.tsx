import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Download,
  Clock,
  Check,
  FileText,
  Layers,
  ArrowRight,
} from 'lucide-react';
import {
  ImportBatch,
  ImportPreviewResult,
  ImportExecuteResult,
  SampleFileInfo,
} from '../types';
import { api } from '../services/api';
import { formatDate } from '../utils/formatters';

interface ImportSettingsPageProps {
  onDataImported: () => void;
}

export const ImportSettingsPage: React.FC<ImportSettingsPageProps> = ({
  onDataImported,
}) => {
  const [importType, setImportType] = useState<string>('finances');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreviewResult | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [executeLoading, setExecuteLoading] = useState(false);
  const [executeResult, setExecuteResult] = useState<ImportExecuteResult | null>(null);

  const [batches, setBatches] = useState<ImportBatch[]>([]);
  const [sampleFiles, setSampleFiles] = useState<SampleFileInfo[]>([]);
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  const loadBatches = async () => {
    try {
      const bList = await api.getImportBatches();
      setBatches(bList);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadBatches();
    api.getSampleFiles().then((s) => setSampleFiles(s));
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setExecuteResult(null);
    setPreviewLoading(true);

    try {
      const res = await api.previewImport(file, importType);
      setPreview(res);
    } catch (err) {
      console.error(err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleExecuteImport = async () => {
    if (!selectedFile) return;
    setExecuteLoading(true);
    try {
      const res = await api.executeImport(selectedFile, importType);
      setExecuteResult(res);
      loadBatches();
      onDataImported();
    } catch (err) {
      console.error(err);
    } finally {
      setExecuteLoading(false);
    }
  };

  const handleResetDemo = async () => {
    setResetLoading(true);
    try {
      await api.resetDemo();
      setResetSuccess(true);
      loadBatches();
      onDataImported();
      setTimeout(() => {
        setResetSuccess(false);
        setResetModalOpen(false);
      }, 1500);
    } catch (err) {
      console.error(err);
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          Импорт файлов и управление данными
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Загрузка исторических таблиц Excel/CSV кофейни и синхронизация аналитических моделей
        </p>
      </div>

      {/* Main Import Workflow Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: File upload & Type Selection (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl bg-[#161F30] border border-[#243045] space-y-5">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-emerald-400" />
              <span>1. Выбор типа данных и загрузка файла</span>
            </h3>

            {/* Type selector pills */}
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-2">
                Тип импортируемых данных:
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {[
                  { id: 'finances', label: 'Финансы (расходы/доходы)' },
                  { id: 'purchases', label: 'История закупок' },
                  { id: 'inventory', label: 'Остатки товаров' },
                  { id: 'supplier_prices', label: 'Прайс-лист поставщика' },
                ].map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => {
                      setImportType(t.id);
                      setPreview(null);
                      setSelectedFile(null);
                      setExecuteResult(null);
                    }}
                    className={`p-3 rounded-xl text-left border text-xs transition ${
                      importType === t.id
                        ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300 font-semibold'
                        : 'bg-[#0B0F17] border-[#243045] text-slate-400 hover:text-white'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Drag & Drop Upload Zone */}
            <div className="border-2 border-dashed border-[#243045] hover:border-emerald-500/50 rounded-2xl p-8 text-center transition bg-[#0B0F17]/50 relative">
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="flex flex-col items-center justify-center gap-2 pointer-events-none">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                  <FileSpreadsheet className="w-6 h-6" />
                </div>
                <div className="text-sm font-semibold text-white">
                  {selectedFile ? selectedFile.name : 'Нажмите или перетащите файл сюда'}
                </div>
                <p className="text-xs text-slate-400">
                  Поддерживаются форматы Microsoft Excel (.xlsx, .xls) и CSV
                </p>
                {selectedFile && (
                  <span className="mt-2 text-xs text-emerald-400 font-mono">
                    Выбран: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} КБ)
                  </span>
                )}
              </div>
            </div>

            {/* Preview Section */}
            {previewLoading && (
              <div className="p-8 text-center text-xs text-slate-400 animate-pulse">
                Чтение и проверка структуры колонок...
              </div>
            )}

            {preview && (
              <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#243045] space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {preview.is_valid ? (
                      <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                        <CheckCircle2 className="w-4 h-4" />
                        {preview.message}
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-xs text-rose-400 font-semibold">
                        <AlertTriangle className="w-4 h-4" />
                        {preview.message}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-slate-400 font-mono">
                    Всего строк: {preview.total_rows}
                  </span>
                </div>

                {/* Headers */}
                <div className="text-[11px] text-slate-400">
                  Обнаруженные колонки:{' '}
                  <span className="text-slate-200 font-mono">
                    {preview.headers_detected.join(', ')}
                  </span>
                </div>

                {/* Sample table */}
                {preview.sample_rows.length > 0 && (
                  <div className="overflow-x-auto rounded-lg border border-[#243045]">
                    <table className="w-full text-[11px] text-left">
                      <thead className="bg-slate-900 text-slate-400">
                        <tr>
                          {preview.headers_detected.map((h, i) => (
                            <th key={i} className="py-2 px-3 font-medium">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#243045] text-slate-300">
                        {preview.sample_rows.map((row, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/20">
                            {preview.headers_detected.map((h, i) => (
                              <td key={i} className="py-1.5 px-3 whitespace-nowrap">
                                {String(row[h] !== undefined ? row[h] : '')}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Confirm Import Action Button */}
                <div className="pt-2 flex justify-end">
                  <button
                    onClick={handleExecuteImport}
                    disabled={!preview.is_valid || executeLoading}
                    className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition disabled:opacity-40"
                  >
                    <Check className="w-4 h-4" />
                    <span>
                      {executeLoading ? 'Импортирование...' : 'Подтвердить импорт в базу данных'}
                    </span>
                  </button>
                </div>
              </div>
            )}

            {/* Execute Result Report */}
            {executeResult && (
              <div
                className={`p-4 rounded-xl border space-y-2 ${
                  executeResult.status === 'success'
                    ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
                    : executeResult.status === 'partial'
                    ? 'bg-amber-950/20 border-amber-500/40 text-amber-300'
                    : 'bg-rose-950/20 border-rose-500/40 text-rose-300'
                }`}
              >
                <div className="flex items-center gap-2 font-bold text-xs">
                  {executeResult.status === 'success' ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <AlertTriangle className="w-4 h-4" />
                  )}
                  <span>{executeResult.message}</span>
                </div>
                <div className="text-xs text-slate-300 font-mono">
                  Загружено строк: {executeResult.rows_imported} / Пропущено (дубликаты): {executeResult.rows_skipped}
                </div>
                {executeResult.errors.length > 0 && (
                  <div className="text-[11px] text-rose-400 space-y-0.5">
                    {executeResult.errors.map((err, i) => (
                      <div key={i}>• {err}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Sample Demo Files & Reset Demo (1 col) */}
        <div className="space-y-6">
          {/* Sample Files Download */}
          <div className="p-6 rounded-2xl bg-[#161F30] border border-[#243045] space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Download className="w-4 h-4 text-emerald-400" />
              <span>Демо-файлы кофейни</span>
            </h3>
            <p className="text-xs text-slate-400">
              Реальные файлы Excel из папки <code className="text-emerald-400">demo_data/</code>. Вы можете скачать любой из них и загрузить для проверки импорта:
            </p>

            <div className="space-y-2.5">
              {sampleFiles.map((sf) => (
                <a
                  key={sf.filename}
                  href={api.downloadSampleUrl(sf.filename)}
                  download={sf.filename}
                  className="p-3 rounded-xl bg-[#0B0F17] hover:bg-slate-800 border border-[#243045] flex items-center justify-between text-xs transition group block"
                >
                  <div>
                    <div className="font-semibold text-white group-hover:text-emerald-400 transition">
                      {sf.filename}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      {sf.description}
                    </div>
                  </div>
                  <Download className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 shrink-0 ml-2" />
                </a>
              ))}
            </div>
          </div>

          {/* Reset Demo State Box */}
          <div className="p-6 rounded-2xl bg-[#161F30] border border-amber-500/20 space-y-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <RotateCcw className="w-4 h-4 text-amber-400" />
              <span>Восстановление демо-состояния</span>
            </h3>
            <p className="text-xs text-slate-400">
              Сброс базы данных и повторный детерминированный посев Cafe Aroma с историческими закупками и ростом цен на кофе +15%.
            </p>
            <button
              onClick={() => setResetModalOpen(true)}
              className="w-full py-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 font-semibold text-xs transition flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Сбросить и восстановить демо</span>
            </button>
          </div>
        </div>
      </div>

      {/* Import History Table */}
      <div className="rounded-2xl bg-[#161F30] border border-[#243045] overflow-hidden">
        <div className="p-4 border-b border-[#243045] text-xs font-bold text-white flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          <span>История пакетных импортов (Import Batches)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#243045] text-slate-400 text-[11px] uppercase tracking-wider bg-[#0F172A]/50">
                <th className="py-3 px-4 font-medium">Файл</th>
                <th className="py-3 px-4 font-medium">Тип данных</th>
                <th className="py-3 px-4 font-medium">Статус</th>
                <th className="py-3 px-4 font-medium text-right">Всего строк</th>
                <th className="py-3 px-4 font-medium text-right">Загружено</th>
                <th className="py-3 px-4 font-medium text-right">Пропущено</th>
                <th className="py-3 px-4 font-medium">Дата импорта</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#243045]/60 text-slate-300">
              {batches.map((b) => (
                <tr key={b.id} className="hover:bg-slate-800/30">
                  <td className="py-3 px-4 font-medium text-white flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5 text-slate-400" />
                    <span>{b.file_name}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-400">{b.import_type}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        b.status === 'success'
                          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20'
                          : 'bg-amber-500/15 text-amber-300 border border-amber-500/20'
                      }`}
                    >
                      {b.status === 'success' ? 'Успешно' : b.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono">{b.rows_total}</td>
                  <td className="py-3 px-4 text-right font-mono text-emerald-400 font-bold">
                    {b.rows_imported}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-slate-500">
                    {b.rows_skipped}
                  </td>
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                    {formatDate(b.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reset Confirmation Modal */}
      {resetModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-md bg-[#161F30] border border-[#243045] rounded-2xl p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <span>Подтверждение сброса демо</span>
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Это действие пересоздаст базу данных SQLite и заполнит её исходным эталонным набором данных Cafe Aroma. Все ваши новые тестовые операции будут возвращены к начальному сценарию.
            </p>

            {resetSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center gap-2">
                <Check className="w-4 h-4" />
                <span>Демо-база Cafe Aroma успешно восстановлена!</span>
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#243045]">
              <button
                type="button"
                onClick={() => setResetModalOpen(false)}
                disabled={resetLoading}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white transition"
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={handleResetDemo}
                disabled={resetLoading}
                className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md transition disabled:opacity-50"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{resetLoading ? 'Сброс...' : 'Сбросить данные'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
