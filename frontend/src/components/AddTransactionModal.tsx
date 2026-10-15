import React, { useState } from 'react';
import { X, Check } from 'lucide-react';
import { api } from '../services/api';

interface AddTransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  categories: string[];
}

export const AddTransactionModal: React.FC<AddTransactionModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  categories,
}) => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState(categories[0] || 'Закупка кофе');
  const [transactionType, setTransactionType] = useState<'expense' | 'income'>('expense');
  const [transactionDate, setTransactionDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description || !amount || parseFloat(amount) <= 0) {
      setError('Заполните описание и укажите положительную сумму');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await api.createTransaction({
        transaction_date: transactionDate,
        description,
        category,
        amount: parseFloat(amount),
        transaction_type: transactionType,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Ошибка сохранения операции');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-[#161F30] border border-[#243045] rounded-2xl shadow-2xl p-5 sm:p-6 max-h-[92dvh] overflow-y-auto">
        <div className="flex items-center justify-between pb-4 border-b border-[#243045]">
          <h3 className="text-base font-bold text-white">Добавить финансовую операцию</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Type Toggle */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Тип операции</label>
            <div className="grid grid-cols-2 gap-2 p-1 rounded-xl bg-[#0B0F17] border border-[#243045]">
              <button
                type="button"
                onClick={() => setTransactionType('expense')}
                className={`py-2 text-xs font-semibold rounded-lg transition ${
                  transactionType === 'expense'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Расход
              </button>
              <button
                type="button"
                onClick={() => setTransactionType('income')}
                className={`py-2 text-xs font-semibold rounded-lg transition ${
                  transactionType === 'income'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Доход
              </button>
            </div>
          </div>

          {/* Date */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Дата операции</label>
            <input
              type="date"
              value={transactionDate}
              onChange={(e) => setTransactionDate(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs focus:outline-none focus:border-emerald-500"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Назначение / Описание</label>
            <input
              type="text"
              placeholder="Например: Закупка сиропов или оплата аренды"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs placeholder:text-slate-600 focus:outline-none focus:border-emerald-500"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Категория</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs focus:outline-none focus:border-emerald-500"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-[#161F30] text-white">
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Amount */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Сумма (₸)</label>
            <input
              type="number"
              placeholder="0.00"
              step="any"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0B0F17] border border-[#243045] text-white text-xs font-mono placeholder:text-slate-600 focus:outline-none focus:border-emerald-500"
              required
            />
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#243045]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white transition"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition disabled:opacity-50"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{loading ? 'Сохранение...' : 'Сохранить'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
