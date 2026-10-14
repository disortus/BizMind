import React, { useState } from 'react';
import { Sparkles, Coffee, ArrowRight, ShieldCheck, FileSpreadsheet, TrendingUp } from 'lucide-react';
import { api } from '../services/api';
import { User } from '../types';

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDemoLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const user = await api.demoLogin();
      onLoginSuccess(user);
    } catch (err: any) {
      setError('Не удалось подключиться к серверу BizMind. Проверьте backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex flex-col justify-center items-center p-6 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 -left-20 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-lg z-10 space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-xl shadow-emerald-500/20">
              <Sparkles className="w-6 h-6 text-slate-950 font-bold" />
            </div>
            <span className="text-3xl font-extrabold text-white tracking-tight">
              BizMind
            </span>
          </div>
          <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold">
            B2B SaaS платформа аналитики и закупок
          </p>
        </div>

        {/* Demo Box */}
        <div className="p-8 rounded-3xl bg-[#161F30] border border-[#243045] shadow-2xl space-y-6">
          <div className="flex items-center gap-3 p-3.5 rounded-2xl bg-[#0B0F17] border border-[#243045]">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
              <Coffee className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <div className="text-xs font-bold text-white">Кофейня «Cafe Aroma»</div>
              <div className="text-[11px] text-slate-400">Демонстрационный аккаунт управляющего</div>
            </div>
          </div>

          <div className="space-y-3 text-xs text-slate-300">
            <div className="font-semibold text-white">Что подготовленo в демонстрации:</div>
            <ul className="space-y-2 text-slate-400 text-[11px]">
              <li className="flex items-start gap-2">
                <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>История за 4 месяца:</strong> 53 финансовые операции и 31 партия закупок</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>Сюжет с ростом цен:</strong> Coffee Roasters поднял цену на зерно до 11 500 ₸ (+15%)</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>Каталог альтернатив:</strong> предложение от Aroma Direct за 10 350 ₸ (−1 150 ₸/кг)</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>Реальный импорт:</strong> готовые Excel-файлы в папке <code className="text-emerald-400">demo_data/</code></span>
              </li>
            </ul>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              {error}
            </div>
          )}

          <button
            onClick={handleDemoLogin}
            disabled={loading}
            className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 shadow-xl shadow-emerald-500/25 transition-all hover:shadow-emerald-500/40 disabled:opacity-50"
          >
            <span>{loading ? 'Вход в аккаунт...' : 'Войти в демо-пространство Cafe Aroma'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <div className="text-center text-[11px] text-slate-500">
            Вход без пароля • Данные хранятся локально в SQLite базе
          </div>
        </div>
      </div>
    </div>
  );
};

function Check(props: any) {
  return (
    <svg
      {...props}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      strokeWidth={2.5}
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
