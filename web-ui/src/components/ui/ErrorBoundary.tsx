import { Component, type ErrorInfo, type ReactNode } from 'react';
import { motion } from 'framer-motion';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });

    // TODO: Send to error tracking service (Sentry, etc.)
    // if (import.meta.env.PROD) {
    //   sendToErrorTracking(error, errorInfo);
    // }
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-md w-full bg-gray-900/50 rounded-2xl p-8 border border-red-500/30 text-center"
          >
            <div className="text-6xl mb-4">😵</div>
            <h1 className="text-2xl font-bold text-white mb-2">
              문제가 발생했습니다
            </h1>
            <p className="text-gray-400 mb-6">
              예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.
            </p>

            {import.meta.env.DEV && this.state.error && (
              <div className="mb-6 text-left">
                <details className="bg-gray-800/50 rounded-lg p-4">
                  <summary className="text-red-400 cursor-pointer font-mono text-sm">
                    오류 상세 정보
                  </summary>
                  <pre className="mt-2 text-xs text-gray-400 overflow-auto max-h-40">
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </details>
              </div>
            )}

            <div className="flex gap-3 justify-center">
              <button
                onClick={this.handleRetry}
                className="px-6 py-2 bg-[#00ff88] text-black font-semibold rounded-lg hover:bg-[#00cc6a] transition-colors"
              >
                다시 시도
              </button>
              <button
                onClick={this.handleReload}
                className="px-6 py-2 bg-gray-700 text-white font-semibold rounded-lg hover:bg-gray-600 transition-colors"
              >
                새로고침
              </button>
            </div>
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Wrapper for functional components
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  fallback?: ReactNode
) {
  return function WithErrorBoundaryWrapper(props: P) {
    return (
      <ErrorBoundary fallback={fallback}>
        <WrappedComponent {...props} />
      </ErrorBoundary>
    );
  };
}
