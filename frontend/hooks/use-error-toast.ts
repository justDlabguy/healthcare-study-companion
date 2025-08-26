import { useToast } from '@/components/ui/use-toast';
import { parseError, getErrorDisplayInfo, type AppError } from '@/lib/error-utils';
import { useCallback } from 'react';

export interface ErrorToastOptions {
  title?: string;
  description?: string;
  duration?: number;
  action?: {
    label: string;
    handler: () => void;
  };
  showRetry?: boolean;
  onRetry?: () => void;
  persistent?: boolean;
}

export function useErrorToast() {
  const { toast, dismiss } = useToast();

  const showError = useCallback((
    error: unknown,
    options: ErrorToastOptions = {}
  ) => {
    const appError = parseError(error);
    const displayInfo = getErrorDisplayInfo(appError, options.onRetry);

    const toastOptions = {
      title: options.title || displayInfo.title,
      description: options.description || displayInfo.message,
      variant: displayInfo.variant,
      duration: options.persistent ? Infinity : (options.duration || 5000),
      action: options.action || displayInfo.action ? {
        altText: displayInfo.action?.label || 'Action',
        children: displayInfo.action?.label || 'Action',
        onClick: displayInfo.action?.handler || (() => {})
      } : undefined
    };

    return toast(toastOptions as any);
  }, [toast]);

  const showNetworkError = useCallback((
    error: unknown,
    options: Omit<ErrorToastOptions, 'title'> = {}
  ) => {
    return showError(error, {
      ...options,
      title: 'Connection Error'
    });
  }, [showError]);

  const showValidationError = useCallback((
    error: unknown,
    options: Omit<ErrorToastOptions, 'title'> = {}
  ) => {
    return showError(error, {
      ...options,
      title: 'Validation Error'
    });
  }, [showError]);

  const showServerError = useCallback((
    error: unknown,
    options: Omit<ErrorToastOptions, 'title'> = {}
  ) => {
    return showError(error, {
      ...options,
      title: 'Server Error'
    });
  }, [showError]);

  const showRetryableError = useCallback((
    error: unknown,
    onRetry: () => void,
    options: Omit<ErrorToastOptions, 'onRetry' | 'showRetry'> = {}
  ) => {
    return showError(error, {
      ...options,
      onRetry,
      showRetry: true
    });
  }, [showError]);

  const showSuccess = useCallback((
    message: string,
    options: { title?: string; duration?: number } = {}
  ) => {
    return toast({
      title: options.title || 'Success',
      description: message,
      variant: 'default'
    });
  }, [toast]);

  const showWarning = useCallback((
    message: string,
    options: { title?: string; duration?: number } = {}
  ) => {
    return toast({
      title: options.title || 'Warning',
      description: message,
      variant: 'destructive' // Using destructive as warning variant
    });
  }, [toast]);

  const showInfo = useCallback((
    message: string,
    options: { title?: string; duration?: number } = {}
  ) => {
    return toast({
      title: options.title || 'Info',
      description: message,
      variant: 'default'
    });
  }, [toast]);

  return {
    showError,
    showNetworkError,
    showValidationError,
    showServerError,
    showRetryableError,
    showSuccess,
    showWarning,
    showInfo,
    dismiss
  };
}