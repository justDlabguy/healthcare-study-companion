import { useState, useCallback, useRef } from 'react';
import { parseError, isRetryableError, getRetryDelay } from '@/lib/error-utils';

export interface RetryOptions {
  maxAttempts?: number;
  baseDelay?: number;
  maxDelay?: number;
  backoffFactor?: number;
  retryCondition?: (error: unknown) => boolean;
  onRetry?: (attempt: number, error: unknown) => void;
  onMaxAttemptsReached?: (error: unknown) => void;
}

export interface RetryState {
  isRetrying: boolean;
  attempt: number;
  lastError: unknown | null;
  canRetry: boolean;
}

export function useRetry<T extends (...args: any[]) => Promise<any>>(
  operation: T,
  options: RetryOptions = {}
) {
  const {
    maxAttempts = 3,
    baseDelay = 1000,
    maxDelay = 30000,
    backoffFactor = 2,
    retryCondition = isRetryableError,
    onRetry,
    onMaxAttemptsReached
  } = options;

  const [state, setState] = useState<RetryState>({
    isRetrying: false,
    attempt: 0,
    lastError: null,
    canRetry: false
  });

  const timeoutRef = useRef<NodeJS.Timeout>();

  const executeWithRetry = useCallback(async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>>> => {
    let currentAttempt = 0;
    let lastError: unknown;

    const attemptOperation = async (): Promise<Awaited<ReturnType<T>>> => {
      currentAttempt++;
      
      setState(prev => ({
        ...prev,
        attempt: currentAttempt,
        isRetrying: currentAttempt > 1
      }));

      try {
        const result = await operation(...args);
        
        // Success - reset state
        setState({
          isRetrying: false,
          attempt: 0,
          lastError: null,
          canRetry: false
        });

        return result;
      } catch (error) {
        lastError = error;
        
        setState(prev => ({
          ...prev,
          lastError: error,
          canRetry: currentAttempt < maxAttempts && retryCondition(error)
        }));

        // Check if we should retry
        if (currentAttempt < maxAttempts && retryCondition(error)) {
          const delay = Math.min(
            baseDelay * Math.pow(backoffFactor, currentAttempt - 1),
            maxDelay
          );

          if (onRetry) {
            onRetry(currentAttempt, error);
          }

          // Wait before retrying
          await new Promise(resolve => {
            timeoutRef.current = setTimeout(resolve, delay);
          });

          return attemptOperation();
        } else {
          // Max attempts reached or error is not retryable
          setState(prev => ({
            ...prev,
            isRetrying: false,
            canRetry: false
          }));

          if (onMaxAttemptsReached && currentAttempt >= maxAttempts) {
            onMaxAttemptsReached(error);
          }

          throw error;
        }
      }
    };

    return attemptOperation();
  }, [operation, maxAttempts, baseDelay, maxDelay, backoffFactor, retryCondition, onRetry, onMaxAttemptsReached]);

  const manualRetry = useCallback(async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>>> => {
    // Reset attempt counter for manual retry
    setState(prev => ({
      ...prev,
      attempt: 0,
      isRetrying: false,
      canRetry: false
    }));

    return executeWithRetry(...args);
  }, [executeWithRetry]);

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = undefined;
    }
    
    setState(prev => ({
      ...prev,
      isRetrying: false,
      canRetry: false
    }));
  }, []);

  const reset = useCallback(() => {
    cancel();
    setState({
      isRetrying: false,
      attempt: 0,
      lastError: null,
      canRetry: false
    });
  }, [cancel]);

  return {
    execute: executeWithRetry,
    retry: manualRetry,
    cancel,
    reset,
    state
  };
}

// Specialized hook for API operations
export function useApiRetry<T extends (...args: any[]) => Promise<any>>(
  apiOperation: T,
  options: Omit<RetryOptions, 'retryCondition'> & {
    retryOnNetworkError?: boolean;
    retryOnServerError?: boolean;
    retryOnRateLimit?: boolean;
  } = {}
) {
  const {
    retryOnNetworkError = true,
    retryOnServerError = true,
    retryOnRateLimit = true,
    ...retryOptions
  } = options;

  const retryCondition = useCallback((error: unknown) => {
    const appError = parseError(error);
    
    // Always retry if the error is marked as retryable
    if (appError.retryable) {
      return true;
    }

    // Custom retry conditions based on error type
    if (retryOnNetworkError && (appError.code === 'NETWORK_ERROR' || appError.code === 'CORS_ERROR')) {
      return true;
    }

    if (retryOnServerError && appError.statusCode && appError.statusCode >= 500) {
      return true;
    }

    if (retryOnRateLimit && appError.code === 'RATE_LIMITED') {
      return true;
    }

    return false;
  }, [retryOnNetworkError, retryOnServerError, retryOnRateLimit]);

  return useRetry(apiOperation, {
    ...retryOptions,
    retryCondition
  });
}

// Hook for file upload operations with retry
export function useUploadRetry<T extends (...args: any[]) => Promise<any>>(
  uploadOperation: T,
  options: RetryOptions = {}
) {
  const retryCondition = useCallback((error: unknown): boolean => {
    const appError = parseError(error);
    
    // Retry on network errors, timeouts, and server errors
    return appError.code === 'NETWORK_ERROR' ||
           appError.code === 'TIMEOUT_ERROR' ||
           appError.code === 'CORS_ERROR' ||
           (appError.statusCode !== undefined && appError.statusCode >= 500);
  }, []);

  return useRetry(uploadOperation, {
    maxAttempts: 3,
    baseDelay: 2000, // Longer delay for uploads
    ...options,
    retryCondition
  });
}