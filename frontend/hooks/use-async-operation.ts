import { useState, useCallback, useRef } from 'react';
import { parseError, type AppError } from '@/lib/error-utils';
import { useErrorToast } from './use-error-toast';
import { useRetry, type RetryOptions } from './use-retry';

export interface AsyncOperationState<T = any> {
  isLoading: boolean;
  error: AppError | null;
  data: T | null;
  progress: number;
  isRetrying: boolean;
  retryCount: number;
}

export interface AsyncOperationOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: AppError) => void;
  onProgress?: (progress: number) => void;
  showToast?: boolean;
  showErrorToast?: boolean;
  showSuccessToast?: boolean;
  successMessage?: string;
  enableRetry?: boolean;
  retryOptions?: RetryOptions;
}

export function useAsyncOperation<T = any>(
  operation: (...args: any[]) => Promise<T>,
  options: AsyncOperationOptions = {}
) {
  const {
    onSuccess,
    onError,
    onProgress,
    showToast = false,
    showErrorToast = true,
    showSuccessToast = false,
    successMessage,
    enableRetry = false,
    retryOptions = {}
  } = options;

  const [state, setState] = useState<AsyncOperationState<T>>({
    isLoading: false,
    error: null,
    data: null,
    progress: 0,
    isRetrying: false,
    retryCount: 0
  });

  const { showError, showSuccess } = useErrorToast();
  const abortControllerRef = useRef<AbortController>();

  // Setup retry mechanism if enabled
  const { execute: executeWithRetry, state: retryState } = useRetry(
    operation,
    enableRetry ? {
      ...retryOptions,
      onRetry: (attempt, error) => {
        setState(prev => ({
          ...prev,
          isRetrying: true,
          retryCount: attempt
        }));
        retryOptions.onRetry?.(attempt, error);
      }
    } : { maxAttempts: 1 }
  );

  const execute = useCallback(async (...args: any[]) => {
    // Cancel any ongoing operation
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
      progress: 0,
      isRetrying: false,
      retryCount: 0
    }));

    try {
      const result = enableRetry 
        ? await executeWithRetry(...args)
        : await operation(...args);
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        data: result,
        progress: 100,
        isRetrying: false
      }));

      if (onSuccess) {
        onSuccess(result);
      }

      if (showSuccessToast && successMessage) {
        showSuccess(successMessage);
      }

      return result;
    } catch (error) {
      // Don't handle error if operation was aborted
      if (abortControllerRef.current?.signal.aborted) {
        return;
      }

      const appError = parseError(error);
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: appError,
        progress: 0,
        isRetrying: false
      }));

      if (onError) {
        onError(appError);
      }

      if (showErrorToast) {
        showError(appError, {
          showRetry: enableRetry && appError.retryable,
          onRetry: () => execute(...args)
        });
      }

      throw error;
    }
  }, [
    operation, 
    executeWithRetry, 
    enableRetry, 
    onSuccess, 
    onError, 
    showErrorToast, 
    showSuccessToast, 
    successMessage, 
    showError, 
    showSuccess
  ]);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    setState(prev => ({
      ...prev,
      isLoading: false,
      isRetrying: false
    }));
  }, []);

  const reset = useCallback(() => {
    cancel();
    setState({
      isLoading: false,
      error: null,
      data: null,
      progress: 0,
      isRetrying: false,
      retryCount: 0
    });
  }, [cancel]);

  const setProgress = useCallback((progress: number) => {
    setState(prev => ({
      ...prev,
      progress: Math.min(Math.max(progress, 0), 100)
    }));
    
    if (onProgress) {
      onProgress(progress);
    }
  }, [onProgress]);

  const retry = useCallback(async (...args: any[]) => {
    return execute(...args);
  }, [execute]);

  return {
    ...state,
    execute,
    retry,
    cancel,
    reset,
    setProgress,
    canRetry: enableRetry && state.error?.retryable === true
  };
}

// Specialized hook for file uploads with progress tracking and retry
export function useFileUpload(options: AsyncOperationOptions = {}) {
  const [uploadState, setUploadState] = useState<{
    isUploading: boolean;
    progress: number;
    error: AppError | null;
    isRetrying: boolean;
  }>({
    isUploading: false,
    progress: 0,
    error: null,
    isRetrying: false
  });

  const { showError } = useErrorToast();

  const uploadFile = useCallback(async (
    file: File,
    uploadFn: (file: File, onProgress?: (progress: number) => void) => Promise<any>
  ) => {
    setUploadState({
      isUploading: true,
      progress: 0,
      error: null,
      isRetrying: false
    });

    try {
      const result = await uploadFn(file, (progress) => {
        setUploadState(prev => ({
          ...prev,
          progress: Math.min(Math.max(progress, 0), 100)
        }));
      });

      setUploadState({
        isUploading: false,
        progress: 100,
        error: null,
        isRetrying: false
      });

      return result;
    } catch (error) {
      const appError = parseError(error);
      
      setUploadState({
        isUploading: false,
        progress: 0,
        error: appError,
        isRetrying: false
      });

      if (options.showErrorToast !== false) {
        showError(appError, {
          title: 'Upload Failed',
          showRetry: appError.retryable,
          onRetry: () => uploadFile(file, uploadFn)
        });
      }

      throw error;
    }
  }, [showError, options.showErrorToast]);

  const resetUpload = useCallback(() => {
    setUploadState({
      isUploading: false,
      progress: 0,
      error: null,
      isRetrying: false
    });
  }, []);

  return {
    ...uploadState,
    uploadFile,
    resetUpload
  };
}

// Hook for API operations with automatic retry and error handling
export function useApiOperation<T = any>(
  apiCall: (...args: any[]) => Promise<T>,
  options: AsyncOperationOptions = {}
) {
  return useAsyncOperation(apiCall, {
    enableRetry: true,
    showErrorToast: true,
    retryOptions: {
      maxAttempts: 3,
      baseDelay: 1000,
      backoffFactor: 2
    },
    ...options
  });
}