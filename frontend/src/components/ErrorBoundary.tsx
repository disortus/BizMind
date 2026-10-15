import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in BizMind UI:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  private handleReturnToCases = () => {
    localStorage.removeItem('bizmind_org_id');
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0B0F17] flex items-center justify-center p-6 text-slate-100">
          <div className="w-full max-w-lg p-8 rounded-3xl bg-[#161F30] border border-[#243045] shadow-2xl text-center space-y-6">
            <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400">
              <AlertTriangle className="w-8 h-8" />
            </div>

            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white tracking-tight">
                Ошибка отображения интерфейса
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                Произошел временный сбой компонента. Вы можете перезагрузить страницу или вернуться к экрану выбора демонстрационного кейса.
              </p>
              {this.state.error && (
                <div className="p-3 rounded-xl bg-[#0B0F17] border border-[#243045] text-left text-[11px] font-mono text-rose-300/90 overflow-x-auto max-h-32">
                  {this.state.error.message}
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleReset}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 transition"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Перезагрузить страницу</span>
              </button>
              <button
                onClick={this.handleReturnToCases}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-[#0B0F17] hover:bg-[#1E293B] border border-[#243045] text-slate-300 font-semibold text-xs flex items-center justify-center gap-2 transition"
              >
                <Home className="w-4 h-4 text-emerald-400" />
                <span>К выбору кейса</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
