import React from 'react';
import { AlertTriangle, ArrowRight, TrendingUp } from 'lucide-react';
import { PriceComparison } from '../types';
import { formatTenge, formatPercent } from '../utils/formatters';

interface PriceAlertBannerProps {
  onGoToComparison: (productId?: number) => void;
  featuredComp?: PriceComparison | null;
}

export const PriceAlertBanner: React.FC<PriceAlertBannerProps> = ({
  onGoToComparison,
  featuredComp,
}) => {
  if (!featuredComp) {
    return null;
  }

  const changePercent = featuredComp.price_change_percent ?? 15.0;
  const isPositiveSpike = changePercent > 0;
  const unit = featuredComp.unit;
  const bestOffer = featuredComp.best_offer;
  const unitDiff = bestOffer ? bestOffer.unit_difference : 0;
  const totDiff = bestOffer ? bestOffer.total_difference : 0;
  const quantity = featuredComp.selected_quantity || 20;

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-rose-950/40 via-[#1E1B2E] to-emerald-950/40 border border-rose-500/30 p-4 sm:p-5 shadow-xl">
      <div className="absolute top-0 right-0 w-72 sm:w-96 h-72 sm:h-96 bg-rose-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center shrink-0 text-rose-400">
            <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
              <span className="px-2 py-0.5 rounded text-[10px] sm:text-[11px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                Обнаружен рост цен {isPositiveSpike ? `+${changePercent}%` : `${changePercent}%`}
              </span>
              <span className="text-[11px] sm:text-xs text-slate-400 truncate">Товар: {featuredComp.product_name}</span>
            </div>
            <h2 className="text-sm sm:text-base font-bold text-white mt-1 leading-snug">
              Поставщик <span className="text-rose-300">{featuredComp.current_supplier_name || 'Текущий поставщик'}</span> поднял цену
              {featuredComp.previous_unit_price
                ? ` с ${formatTenge(featuredComp.previous_unit_price)} до ${formatTenge(featuredComp.current_unit_price)}/${unit}`
                : ` до ${formatTenge(featuredComp.current_unit_price)}/${unit}`}
            </h2>
            {bestOffer && (
              <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
                В каталоге найдено сопоставимое предложение от{' '}
                <span className="text-emerald-400 font-semibold">{bestOffer.supplier_name}</span> за{' '}
                <span className="text-emerald-400 font-semibold">{formatTenge(bestOffer.offered_price)}/{unit}</span>. 
                Потенциальная разница: <strong className="text-white">{formatTenge(unitDiff)} на {unit}</strong>
                {' '}(до <strong className="text-emerald-300">{formatTenge(totDiff)}</strong> на закупку {quantity} {unit}).
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0 w-full md:w-auto">
          <button
            onClick={() => onGoToComparison(featuredComp.product_id)}
            className="w-full md:w-auto justify-center px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all hover:translate-x-0.5"
          >
            <span>Сравнить предложения</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
