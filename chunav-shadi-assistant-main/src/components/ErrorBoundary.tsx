import { Component, type ErrorInfo, type ReactNode } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, RefreshCw, Home, Bug } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleRetry = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = "/";
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex min-h-screen items-center justify-center bg-navy px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="relative w-full max-w-md overflow-hidden rounded-3xl border border-gold/20 bg-navy/80 p-8 shadow-glow"
          >
            {/* Decorative elements */}
            <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-gradient-to-br from-saffron to-gold opacity-20 blur-3xl" />
            <div className="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-gradient-to-br from-rose-gold to-gold opacity-20 blur-3xl" />

            <div className="relative text-center">
              {/* Icon */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full border-2 border-gold/30 bg-navy/50"
              >
                <span className="text-4xl">🤔</span>
              </motion.div>

              {/* Title */}
              <h1 className="font-display text-3xl font-bold text-gradient-gold">
                Oops! Kuch toh gadbad hai.
              </h1>

              {/* Subtitle */}
              <p className="mt-3 text-sm leading-relaxed text-cream/70">
                Something went wrong on our end. Backend chalu hai na? 🤔
              </p>

              {/* Error details (dev mode) */}
              {import.meta.env.DEV && this.state.error && (
                <div className="mt-6 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-left">
                  <div className="flex items-center gap-2 text-destructive">
                    <Bug className="h-4 w-4" />
                    <span className="text-xs font-semibold uppercase tracking-wider">Error Details</span>
                  </div>
                  <pre className="mt-2 max-h-32 overflow-auto text-xs text-destructive/80">
                    {this.state.error.message}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </div>
              )}

              {/* Action buttons */}
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={this.handleRetry}
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-mandap px-6 py-3 font-semibold text-navy shadow-gold gold-shimmer"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={this.handleGoHome}
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-gold/40 bg-navy/40 px-6 py-3 font-semibold text-gold transition hover:bg-gold/10"
                >
                  <Home className="h-4 w-4" />
                  Wapas Mandap
                </motion.button>
              </div>

              {/* Help text */}
              <p className="mt-6 text-xs text-cream/40">
                Still facing issues? Check if the backend server is running on port 8000.
              </p>
            </div>
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Simple error fallback for smaller components
export function ErrorFallback({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-2xl border border-destructive/30 bg-destructive/10 p-6 text-center"
    >
      <AlertTriangle className="mx-auto mb-3 h-10 w-10 text-destructive" />
      <h3 className="font-display text-lg text-destructive">Something went wrong</h3>
      <p className="mt-2 text-sm text-cream/70">
        {error.message || "An unexpected error occurred"}
      </p>
      <button
        onClick={reset}
        className="mt-4 inline-flex items-center gap-2 rounded-full bg-mandap px-4 py-2 text-sm font-semibold text-navy"
      >
        <RefreshCw className="h-4 w-4" />
        Try Again
      </button>
    </motion.div>
  );
}
