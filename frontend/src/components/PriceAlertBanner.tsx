import React from 'react';
import { AlertTriangle, ArrowRight, TrendingUp, Sparkles, CheckCircle } from 'lucide-react';
import { formatTenge } from '../utils/formatters';

interface PriceAlertBannerProps {
  onGoToComparison: () => void;
}

export const PriceAlertBanner: React.FC<PriceAlertBannerProps> = ({ onGoToComparison }) => {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-rose-950/40 via-[#1E1B2E] to-emerald-950/40 border border-rose-500/30 p-5 shadow-xl">
      <div className="absolute top-0 right-0 w-96 h-96 bg-rose-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center shrink-0 text-rose-400">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Обнаружен рост цен +15.0%
              </span>
              <span className="text-xs text-slate-400">Товар: Кофе в зернах Espresso Blend</span>
            </div>
            <h2 className="text-base font-bold text-white mt-1">
              Поставщик <span className="text-rose-300">Coffee Roasters Hub</span> поднял цену с 10 000 ₸ до 11 500 ₸/кг
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              В моковом каталоге найдено сопоставимое предложение от <span className="text-emerald-400 font-semibold">Aroma Direct</span> за <span className="text-emerald-400 font-semibold">10 350 ₸/кг</span>. 
              Потенциальная разница составляет <strong className="text-white">1 150 ₸ на кг</strong> (до <strong className="text-emerald-300">23 000 ₸</strong> на закупку 20 кг).
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={onGoToComparison}
            className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all hover:translate-x-0.5"
          >
            <span>Сравнить поставщиков</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
