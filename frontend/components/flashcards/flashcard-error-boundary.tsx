"use client";

import React, { Component, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Clock, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface ErrorInfo {
  componentStack: string;
  errorBoundary?: string;
}

interface FlashcardErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  retryCount: number;
  isRetrying: boolean;
  gracefulError?: {
    error_id: string;
    message: string;
    fallback_available: boolean;
    recovery_actions: string[];
    retry_after?: number;
    degradation_mode?: string;
  };
}

interface FlashcardErrorBoundaryProps {
  children: ReactNode;
  onRetry?: () => void;
  onFallback?: () => void;
  maxRetries?: number;
}

export class FlashcardErrorBoundary extends Component<
  FlashcardErrorBoundaryProps,
  FlashcardErrorBoundaryState
> {
  private retryTimer: NodeJS.Timeout | null = null;

  constructor(props: FlashcardErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      isRetrying: false,
    };
  }

  static getDerivedStateFromError(
    error: Error
  ): Partial<FlashcardErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("FlashcardErrorBoundary caught an error:", error, errorInfo);

    // Check if this is a graceful degradation error
    if (error.message && error.message.includes("fallback_available")) {
      try {
        const gracefulError = JSON.parse(error.message);
        this.setState({ gracefulError });
      } catch (e) {
        // Not a graceful error, continue with normal error handling
      }
    }

    this.setState({
      error,
      errorInfo,
    });
  }

  handleRetry = () => {
    const { maxRetries = 3 } = this.props;

    if (this.state.retryCount >= maxRetries) {
      return;
    }

    this.setState({ isRetrying: true });

    // If there's a retry_after time, wait for it
    const retryDelay = this.state.gracefulError?.retry_after
      ? this.state.gracefulError.retry_after * 1000
      : 2000; // Default 2 seconds

    this.retryTimer = setTimeout(() => {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: this.state.retryCount + 1,
        isRetrying: false,
        gracefulError: undefined,
      });

      if (this.props.onRetry) {
        this.props.onRetry();
      }
    }, retryDelay);
  };

  handleFallback = () => {
    if (this.props.onFallback) {
      this.props.onFallback();
    }

    // Reset error state to allow fallback content to render
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      gracefulError: undefined,
    });
  };

  componentWillUnmount() {
    if (this.retryTimer) {
      clearTimeout(this.retryTimer);
    }
  }

  renderGracefulError() {
    const { gracefulError, retryCount, isRetrying } = this.state;
    const { maxRetries = 3 } = this.props;

    if (!gracefulError) return null;

    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            AI Service Temporarily Unavailable
          </CardTitle>
          <CardDescription>
            Don't worry - we can still help you create flashcards!
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <HelpCircle className="h-4 w-4" />
            <AlertTitle>What happened?</AlertTitle>
            <AlertDescription>{gracefulError.message}</AlertDescription>
          </Alert>

          {gracefulError.fallback_available && (
            <Alert className="border-blue-200 bg-blue-50">
              <AlertTitle className="text-blue-800">Good news!</AlertTitle>
              <AlertDescription className="text-blue-700">
                We can still create flashcards for you using our backup system.
                The flashcards will be based on your content and will help you
                study effectively.
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <h4 className="font-medium">What you can do:</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              {gracefulError.recovery_actions.map((action, index) => (
                <li key={index}>{action}</li>
              ))}
            </ul>
          </div>

          <div className="flex gap-2 flex-wrap">
            {gracefulError.fallback_available && (
              <Button
                onClick={this.handleFallback}
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Use Backup System
              </Button>
            )}

            {retryCount < maxRetries && (
              <Button
                variant="outline"
                onClick={this.handleRetry}
                disabled={isRetrying}
                className="flex items-center gap-2"
              >
                {isRetrying ? (
                  <>
                    <Clock className="h-4 w-4 animate-spin" />
                    Retrying...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    Try Again ({maxRetries - retryCount} attempts left)
                  </>
                )}
              </Button>
            )}
          </div>

          {gracefulError.error_id && (
            <div className="text-xs text-gray-500 mt-4">
              Error ID: {gracefulError.error_id}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  renderGenericError() {
    const { error, retryCount, isRetrying } = this.state;
    const { maxRetries = 3 } = this.props;

    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            Something went wrong
          </CardTitle>
          <CardDescription>
            We encountered an unexpected error while generating your flashcards.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert variant="destructive">
            <AlertTitle>Error Details</AlertTitle>
            <AlertDescription>
              {error?.message || "An unknown error occurred"}
            </AlertDescription>
          </Alert>

          <div className="space-y-2">
            <h4 className="font-medium">What you can try:</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              <li>Refresh the page and try again</li>
              <li>Try with shorter content</li>
              <li>Check your internet connection</li>
              <li>Contact support if the problem persists</li>
            </ul>
          </div>

          <div className="flex gap-2">
            {retryCount < maxRetries && (
              <Button
                onClick={this.handleRetry}
                disabled={isRetrying}
                className="flex items-center gap-2"
              >
                {isRetrying ? (
                  <>
                    <Clock className="h-4 w-4 animate-spin" />
                    Retrying...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    Try Again ({maxRetries - retryCount} attempts left)
                  </>
                )}
              </Button>
            )}

            <Button variant="outline" onClick={() => window.location.reload()}>
              Refresh Page
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  render() {
    if (this.state.hasError) {
      return this.state.gracefulError
        ? this.renderGracefulError()
        : this.renderGenericError();
    }

    return this.props.children;
  }
}

export default FlashcardErrorBoundary;
