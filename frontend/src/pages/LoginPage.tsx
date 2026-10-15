import React, { useState } from 'react';
import { Sparkles, Coffee, Store, ArrowRight, CheckCircle2, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { User } from '../types';

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [loadingOrgId, setLoadingOrgId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (orgId: number) => {
    setLoadingOrgId(orgId);
    setError(null);
    try {
      const user = await api.demoLogin(orgId);
      onLoginSuccess(user);
    } catch (err: any) {
      setError('Не удалось подключиться к серверу BizMind. Проверьте запущенный backend.');
    } finally {
      setLoadingOrgId(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex flex-col justify-center items-center p-4 sm:p-6 py-8 sm:py-12 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 -left-24 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 -right-24 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-4xl z-10 space-y-6 sm:space-y-8">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2.5 sm:gap-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-xl shadow-emerald-500/20">
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-slate-950 font-bold" />
            </div>
            <span className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              BizMind
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Demo Platform
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Платформа финансовой аналитики и оперативной оптимизации закупок малого бизнеса
          </p>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#161F30] border border-[#243045] text-[11px] sm:text-xs text-slate-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Выберите демонстрационное пространство для старта</span>
          </div>
        </div>

        {error && (
          <div className="max-w-md mx-auto p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs text-center">
            {error}
          </div>
        )}

        {/* Demo Cases Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          {/* CASE A: Cafe Aroma */}
          <div className="p-5 sm:p-6 rounded-3xl bg-[#161F30] border border-[#243045] hover:border-emerald-500/40 transition-all flex flex-col justify-between shadow-2xl relative group">
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 sm:gap-0">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
                    <Coffee className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white group-hover:text-emerald-300 transition">
                      Кофейня «Cafe Aroma»
                    </h3>
                    <p className="text-[11px] text-slate-400">ул. Абая 45 • Алексей Смирнов</p>
                  </div>
                </div>
                <span className="self-start sm:self-auto text-[10px] font-bold px-2 py-1 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  Первоначальное внедрение
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#0B0F17]/60 border border-[#1E293B] text-xs text-slate-300 leading-relaxed">
                Сценарий миграции: до BizMind учёт вёлся в Excel. Демонстрация первой загрузки таблиц, обнаружения скрытого роста цен на кофе (+15%) и моментального подбора альтернатив.
              </div>

              <div className="space-y-2 text-[11px] text-slate-400">
                <div className="font-semibold text-slate-200">Ключевые данные сценария:</div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Рост цены кофе:</strong> скачок с 10 000 до 11 500 ₸ (+15%)</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Альтернатива Aroma Direct:</strong> 10 350 ₸ (−1 150 ₸/кг, выгода 23 000 ₸ на 20 кг)</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Критический остаток:</strong> молоко 3.2% (12 л при норме 25 л)</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Импорт Excel:</strong> 4 готовых файла в папке <code className="text-emerald-400">demo_data/</code></span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleLogin(1)}
              disabled={loadingOrgId !== null}
              className="mt-6 w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50"
            >
              <span>{loadingOrgId === 1 ? 'Подключение...' : 'Войти в кейс Cafe Aroma (Внедрение)'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* CASE B: Daily Cup */}
          <div className="p-5 sm:p-6 rounded-3xl bg-[#161F30] border border-[#243045] hover:border-teal-500/40 transition-all flex flex-col justify-between shadow-2xl relative group">
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 sm:gap-0">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center shrink-0">
                    <Store className="w-5 h-5 text-teal-400" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white group-hover:text-teal-300 transition">
                      Сеть «Daily Cup»
                    </h3>
                    <p className="text-[11px] text-slate-400">ул. Достык 89 • Данияр Касымов</p>
                  </div>
                </div>
                <span className="self-start sm:self-auto text-[10px] font-bold px-2 py-1 rounded-full bg-teal-500/15 text-teal-300 border border-teal-500/30">
                  Регулярное использование
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#0B0F17]/60 border border-[#1E293B] text-xs text-slate-300 leading-relaxed">
                Сценарий системной работы: кофейня формата To-Go использует BizMind 5+ месяцев. Контроль повторяющихся закупок упаковки, предотвращение дефицита расходников и оптимизация маржи.
              </div>

              <div className="space-y-2 text-[11px] text-slate-400">
                <div className="font-semibold text-slate-200">Ключевые данные сценария:</div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
                  <span><strong>Рост цен упаковки:</strong> стаканы Kraft 250мл с 1 200 до 1 420 ₸ (+18.3%)</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
                  <span><strong>Альтернатива EcoTorg:</strong> 1 230 ₸ (−190 ₸/упак, бесплатная доставка)</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
                  <span><strong>Критический остаток:</strong> держатели стаканов (6 упак при норме 12)</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
                  <span><strong>5 месяцев истории:</strong> стабильный поток финансов и динамика поставщиков</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleLogin(2)}
              disabled={loadingOrgId !== null}
              className="mt-6 w-full py-3 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-teal-500/20 transition-all disabled:opacity-50"
            >
              <span>{loadingOrgId === 2 ? 'Подключение...' : 'Войти в кейс Daily Cup (Регулярный)'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Footer info */}
        <div className="text-center text-xs text-slate-500 space-y-1">
          <div>Переключение между кофейнями доступно в любой момент внутри интерфейса приложения.</div>
          <div className="text-[11px] text-slate-600">
            Данные каждого пространства строго изолированы • Хранение в постоянном SQLite хранилище
          </div>
        </div>
      </div>
    </div>
  );
};
