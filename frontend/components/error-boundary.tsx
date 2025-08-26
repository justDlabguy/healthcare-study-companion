'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { parseError, logError, type AppError } from '@/lib/error-utils';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorId?: string;
  appError?: AppError;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; appError?: AppError; resetError: () => void }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  showErrorDetails?: boolean;
  level?: 'page' | 'component' | 'section';
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private retryCount = 0;
  private maxRetries = 3;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const appError = parseError(error);
    
    return { 
      hasError: true, 
      error, 
      errorId,
      appError
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const { appError, errorId } = this.state;
    
    // Log the error
    if (appError) {
      logError(appError, `ErrorBoundary-${errorId}`);
    }

    console.error('Error caught by boundary:', {
      error,
      errorInfo,
      errorId,
      retryCount: this.retryCount,
      componentStack: errorInfo.componentStack
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, you might want to send this to an error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Example: Send to error tracking service
      // errorTrackingService.captureException(error, {
      //   tags: { errorBoundary: true, level: this.props.level },
      //   extra: { errorInfo, errorId }
      // });
    }
  }

  resetError = () => {
    this.retryCount++;
    this.setState({ hasError: false, error: undefined, errorId: undefined, appError: undefined });
  };

  handleRefresh = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  handleReportError = () => {
    const { error, errorId, appError } = this.state;
    const errorReport = {
      errorId,
      message: error?.message,
      stack: error?.stack,
      appError,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    };

    // Copy error report to clipboard
    navigator.clipboard.writeText(JSON.stringify(errorReport, null, 2)).then(() => {
      alert('Error report copied to clipboard. Please send this to support.');
    }).catch(() => {
      console.error('Failed to copy error report:', errorReport);
      alert('Failed to copy error report. Please check the console for details.');
    });
  };

  render() {
    if (this.state.hasError) {
      const { error, appError, errorId } = this.state;
      const { fallback: FallbackComponent, level = 'component', showErrorDetails = false } = this.props;

      if (FallbackComponent) {
        return <FallbackComponent error={error} appError={appError} resetError={this.resetError} />;
      }

      // Different layouts based on error boundary level
      if (level === 'page') {
        return (
          <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
            <Card className="w-full max-w-lg">
              <CardHeader className="text-center">
                <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
                <CardTitle className="text-xl text-red-600">Something went wrong</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-600 text-center">
                  {appError?.message || 'We encountered an unexpected error. Please try again or contact support if the problem persists.'}
                </p>
                
                {showErrorDetails && error && (
                  <details className="bg-gray-100 p-3 rounded text-sm">
                    <summary className="cursor-pointer font-medium text-gray-700 mb-2">
                      Technical Details
                    </summary>
                    <div className="space-y-2 text-xs text-gray-600">
                      <div><strong>Error ID:</strong> {errorId}</div>
                      <div><strong>Message:</strong> {error.message}</div>
                      {error.stack && (
                        <div>
                          <strong>Stack:</strong>
                          <pre className="mt-1 whitespace-pre-wrap break-all">{error.stack}</pre>
                        </div>
                      )}
                    </div>
                  </details>
                )}

                <div className="flex flex-col sm:flex-row gap-2">
                  <Button onClick={this.resetError} variant="outline" className="flex-1">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again
                  </Button>
                  <Button onClick={this.handleRefresh} className="flex-1">
                    Refresh Page
                  </Button>
                </div>

                <div className="flex flex-col sm:flex-row gap-2">
                  <Button onClick={this.handleGoHome} variant="outline" className="flex-1">
                    <Home className="w-4 h-4 mr-2" />
                    Go Home
                  </Button>
                  <Button onClick={this.handleReportError} variant="outline" className="flex-1">
                    <Bug className="w-4 h-4 mr-2" />
                    Report Error
                  </Button>
                </div>

                {this.retryCount > 0 && (
                  <p className="text-xs text-gray-500 text-center">
                    Retry attempts: {this.retryCount}/{this.maxRetries}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        );
      }

      if (level === 'section') {
        return (
          <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-red-800 mb-1">
                  Section Error
                </h3>
                <p className="text-sm text-red-700 mb-3">
                  {appError?.message || 'This section encountered an error.'}
                </p>
                <div className="flex gap-2">
                  <Button onClick={this.resetError} size="sm" variant="outline">
                    <RefreshCw className="w-3 h-3 mr-1" />
                    Retry
                  </Button>
                  {showErrorDetails && (
                    <Button onClick={this.handleReportError} size="sm" variant="outline">
                      <Bug className="w-3 h-3 mr-1" />
                      Report
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      }

      // Component level (default)
      return (
        <div className="p-6 text-center border border-red-200 bg-red-50 rounded-lg">
          <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-red-800 mb-2">Component Error</h3>
          <p className="text-red-700 mb-4">
            {appError?.message || 'This component encountered an error.'}
          </p>
          <div className="flex justify-center gap-2">
            <Button onClick={this.resetError} size="sm" variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
            {showErrorDetails && (
              <Button onClick={this.handleReportError} size="sm" variant="outline">
                <Bug className="w-4 h-4 mr-2" />
                Report
              </Button>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

// Hook version for functional components
export function useErrorHandler() {
  return (error: Error, errorInfo?: React.ErrorInfo) => {
    const appError = parseError(error);
    logError(appError, 'useErrorHandler');
    
    console.error('Error handled:', error, errorInfo);
    
    // In production, send to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // errorTrackingService.captureException(error, { extra: errorInfo });
    }
  };
}

// Specialized error fallback components
export function SimpleErrorFallback({ 
  error, 
  appError, 
  resetError 
}: { 
  error?: Error; 
  appError?: AppError;
  resetError: () => void;
}) {
  return (
    <div className="text-center p-8">
      <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-red-600 mb-4">Oops! Something went wrong</h2>
      <p className="text-gray-600 mb-4">
        {appError?.message || 'We\'re sorry, but something unexpected happened. Please try again.'}
      </p>
      <Button onClick={resetError}>
        <RefreshCw className="w-4 h-4 mr-2" />
        Try Again
      </Button>
    </div>
  );
}

export function NetworkErrorFallback({ 
  error, 
  appError, 
  resetError 
}: { 
  error?: Error; 
  appError?: AppError;
  resetError: () => void;
}) {
  return (
    <div className="text-center p-8">
      <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <AlertTriangle className="w-8 h-8 text-yellow-600" />
      </div>
      <h2 className="text-xl font-semibold text-yellow-600 mb-4">Connection Problem</h2>
      <p className="text-gray-600 mb-4">
        {appError?.message || 'Unable to connect to the server. Please check your internet connection.'}
      </p>
      <div className="flex justify-center gap-2">
        <Button onClick={resetError} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Try Again
        </Button>
        <Button onClick={() => window.location.reload()}>
          Refresh Page
        </Button>
      </div>
    </div>
  );
}