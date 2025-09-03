"use client";

import { useState, useCallback, useRef } from "react";
import { useToast } from "@/components/ui/use-toast";

interface GracefulError {
  error_id: string;
  message: string;
  fallback_available: boolean;
  recovery_actions: string[];
  retry_after?: number;
  degradation_mode?: string;
  suggestions?: string[];
}

interface DegradationState {
  isUsingFallback: boolean;
  lastError: GracefulError | null;
  retryCount: number;
  canRetry: boolean;
  isRetrying: boolean;
}

interface UseGracefulDegradationOptions {
  maxRetries?: number;
  onFallback?: (error: GracefulError) => void;
  onRecovery?: () => void;
  showToasts?: boolean;
}

export function useGracefulDegradation(
  options: UseGracefulDegradationOptions = {}
) {
  const { maxRetries = 3, onFallback, onRecovery, showToasts = true } = options;
  const { toast } = useToast();

  const [state, setState] = useState<DegradationState>({
    isUsingFallback: false,
    lastError: null,
    retryCount: 0,
    canRetry: true,
    isRetrying: false,
  });

  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleError = useCallback(
    (error: any) => {
      // Check if this is a graceful degradation error
      let gracefulError: GracefulError | null = null;

      if (error?.response?.status === 206) {
        // Partial content - fallback was used
        gracefulError = error.response.data;
      } else if (
        error?.response?.status === 503 &&
        error?.response?.data?.fallback_available
      ) {
        // Service unavailable but fallback available
        gracefulError = error.response.data;
      } else if (
        error?.message &&
        typeof error.message === "object" &&
        error.message.fallback_available !== undefined
      ) {
        // Direct graceful error object
        gracefulError = error.message;
      }

      if (gracefulError) {
        setState((prev) => ({
          ...prev,
          isUsingFallback: gracefulError!.fallback_available,
          lastError: gracefulError,
          canRetry: prev.retryCount < maxRetries,
        }));

        if (showToasts) {
          if (gracefulError.fallback_available) {
            toast({
              title: "Using Backup System",
              description: gracefulError.message,
              variant: "default",
            });
          } else {
            toast({
              title: "Service Unavailable",
              description: gracefulError.message,
              variant: "destructive",
            });
          }
        }

        if (gracefulError.fallback_available && onFallback) {
          onFallback(gracefulError);
        }

        return true; // Handled gracefully
      }

      return false; // Not a graceful error
    },
    [maxRetries, onFallback, showToasts]
  );

  const retry = useCallback(
    async (retryFn: () => Promise<any>) => {
      if (!state.canRetry || state.isRetrying) {
        return;
      }

      setState((prev) => ({
        ...prev,
        isRetrying: true,
      }));

      const retryDelay = state.lastError?.retry_after
        ? state.lastError.retry_after * 1000
        : Math.min(1000 * Math.pow(2, state.retryCount), 10000); // Exponential backoff, max 10s

      try {
        if (retryDelay > 0) {
          await new Promise((resolve) => {
            retryTimeoutRef.current = setTimeout(resolve, retryDelay);
          });
        }

        const result = await retryFn();

        // Success - reset state
        setState({
          isUsingFallback: false,
          lastError: null,
          retryCount: 0,
          canRetry: true,
          isRetrying: false,
        });

        if (showToasts && state.isUsingFallback) {
          toast({
            title: "Service Restored",
            description: "AI service is working normally again.",
            variant: "default",
          });
        }

        if (onRecovery) {
          onRecovery();
        }

        return result;
      } catch (error) {
        const wasHandled = handleError(error);

        setState((prev) => ({
          ...prev,
          retryCount: prev.retryCount + 1,
          canRetry: prev.retryCount + 1 < maxRetries,
          isRetrying: false,
        }));

        if (!wasHandled) {
          throw error; // Re-throw if not handled gracefully
        }
      }
    },
    [state, maxRetries, handleError, onRecovery, showToasts]
  );

  const reset = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }

    setState({
      isUsingFallback: false,
      lastError: null,
      retryCount: 0,
      canRetry: true,
      isRetrying: false,
    });
  }, []);

  const acceptFallback = useCallback(() => {
    setState((prev) => ({
      ...prev,
      canRetry: false, // Stop offering retries
    }));

    if (showToasts) {
      toast({
        title: "Using Backup System",
        description: "We'll continue with our backup system for now.",
        variant: "default",
      });
    }
  }, [showToasts]);

  return {
    ...state,
    handleError,
    retry,
    reset,
    acceptFallback,

    // Helper methods
    isHealthy: !state.isUsingFallback && !state.lastError,
    hasRecoveryOptions: (state.lastError?.recovery_actions?.length ?? 0) > 0,
    recoveryActions: state.lastError?.recovery_actions || [],
    errorMessage: state.lastError?.message,
    errorId: state.lastError?.error_id,
  };
}

export type { GracefulError, DegradationState };
