import { AxiosError } from 'axios';

export interface AppError {
  message: string;
  code?: string;
  statusCode?: number;
  details?: any;
  timestamp: string;
  retryable: boolean;
}

export interface ErrorDisplayInfo {
  title: string;
  message: string;
  variant: 'destructive' | 'warning' | 'default';
  action?: {
    label: string;
    handler: () => void;
  };
}

/**
 * Parse different types of errors into a standardized AppError format
 */
export function parseError(error: unknown): AppError {
  const timestamp = new Date().toISOString();

  // Handle Axios errors (API errors)
  if (error instanceof AxiosError) {
    const statusCode = error.response?.status;
    const responseData = error.response?.data;
    
    // Handle specific HTTP status codes
    switch (statusCode) {
      case 400:
        return {
          message: responseData?.detail || 'Invalid request. Please check your input.',
          code: 'BAD_REQUEST',
          statusCode,
          details: responseData,
          timestamp,
          retryable: false
        };
      
      case 401:
        return {
          message: 'Your session has expired. Please log in again.',
          code: 'UNAUTHORIZED',
          statusCode,
          details: responseData,
          timestamp,
          retryable: false
        };
      
      case 403:
        return {
          message: 'You don\'t have permission to perform this action.',
          code: 'FORBIDDEN',
          statusCode,
          details: responseData,
          timestamp,
          retryable: false
        };
      
      case 404:
        return {
          message: 'The requested resource was not found.',
          code: 'NOT_FOUND',
          statusCode,
          details: responseData,
          timestamp,
          retryable: false
        };
      
      case 409:
        return {
          message: responseData?.detail || 'A conflict occurred. The resource may have been modified.',
          code: 'CONFLICT',
          statusCode,
          details: responseData,
          timestamp,
          retryable: true
        };
      
      case 422:
        return {
          message: responseData?.detail || 'Validation error. Please check your input.',
          code: 'VALIDATION_ERROR',
          statusCode,
          details: responseData,
          timestamp,
          retryable: false
        };
      
      case 429:
        return {
          message: 'Too many requests. Please wait a moment and try again.',
          code: 'RATE_LIMITED',
          statusCode,
          details: responseData,
          timestamp,
          retryable: true
        };
      
      case 500:
        return {
          message: 'A server error occurred. Please try again later.',
          code: 'INTERNAL_SERVER_ERROR',
          statusCode,
          details: responseData,
          timestamp,
          retryable: true
        };
      
      case 502:
      case 503:
      case 504:
        return {
          message: 'The service is temporarily unavailable. Please try again later.',
          code: 'SERVICE_UNAVAILABLE',
          statusCode,
          details: responseData,
          timestamp,
          retryable: true
        };
      
      default:
        return {
          message: responseData?.detail || error.message || 'An unexpected error occurred.',
          code: 'UNKNOWN_HTTP_ERROR',
          statusCode,
          details: responseData,
          timestamp,
          retryable: statusCode ? statusCode >= 500 : true
        };
    }
  }

  // Handle network errors
  if (error instanceof Error) {
    if (error.message.includes('Network Error') || error.message.includes('ERR_NETWORK')) {
      return {
        message: 'Network connection failed. Please check your internet connection.',
        code: 'NETWORK_ERROR',
        details: { originalMessage: error.message },
        timestamp,
        retryable: true
      };
    }

    if (error.message.includes('timeout')) {
      return {
        message: 'The request timed out. Please try again.',
        code: 'TIMEOUT_ERROR',
        details: { originalMessage: error.message },
        timestamp,
        retryable: true
      };
    }

    // Handle CORS errors
    if (error.message.includes('CORS') || error.message.includes('cross-origin')) {
      return {
        message: 'Connection to server failed. Please try refreshing the page.',
        code: 'CORS_ERROR',
        details: { originalMessage: error.message },
        timestamp,
        retryable: true
      };
    }

    return {
      message: error.message,
      code: 'GENERIC_ERROR',
      details: { originalMessage: error.message, stack: error.stack },
      timestamp,
      retryable: false
    };
  }

  // Handle string errors
  if (typeof error === 'string') {
    return {
      message: error,
      code: 'STRING_ERROR',
      timestamp,
      retryable: false
    };
  }

  // Handle unknown errors
  return {
    message: 'An unexpected error occurred. Please try again.',
    code: 'UNKNOWN_ERROR',
    details: error,
    timestamp,
    retryable: false
  };
}

/**
 * Convert an AppError to user-friendly display information
 */
export function getErrorDisplayInfo(error: AppError, retryHandler?: () => void): ErrorDisplayInfo {
  const baseInfo: ErrorDisplayInfo = {
    title: 'Error',
    message: error.message,
    variant: 'destructive'
  };

  // Add retry action for retryable errors
  if (error.retryable && retryHandler) {
    baseInfo.action = {
      label: 'Retry',
      handler: retryHandler
    };
  }

  // Customize based on error code
  switch (error.code) {
    case 'UNAUTHORIZED':
      return {
        ...baseInfo,
        title: 'Authentication Required',
        action: {
          label: 'Login',
          handler: () => window.location.href = '/auth/login'
        }
      };

    case 'FORBIDDEN':
      return {
        ...baseInfo,
        title: 'Access Denied',
        variant: 'warning'
      };

    case 'NOT_FOUND':
      return {
        ...baseInfo,
        title: 'Not Found',
        variant: 'warning'
      };

    case 'VALIDATION_ERROR':
      return {
        ...baseInfo,
        title: 'Validation Error',
        variant: 'warning'
      };

    case 'RATE_LIMITED':
      return {
        ...baseInfo,
        title: 'Rate Limited',
        message: 'Too many requests. Please wait a moment before trying again.',
        variant: 'warning'
      };

    case 'NETWORK_ERROR':
    case 'CORS_ERROR':
      return {
        ...baseInfo,
        title: 'Connection Error',
        variant: 'warning'
      };

    case 'TIMEOUT_ERROR':
      return {
        ...baseInfo,
        title: 'Request Timeout',
        variant: 'warning'
      };

    case 'SERVICE_UNAVAILABLE':
      return {
        ...baseInfo,
        title: 'Service Unavailable',
        message: 'The service is temporarily unavailable. Please try again in a few minutes.',
        variant: 'warning'
      };

    default:
      return baseInfo;
  }
}

/**
 * Check if an error is a CORS error
 */
export function isCorsError(error: unknown): boolean {
  if (error instanceof AxiosError) {
    return error.code === 'ERR_NETWORK' && !error.response;
  }
  
  if (error instanceof Error) {
    return error.message.includes('CORS') || 
           error.message.includes('cross-origin') ||
           error.message.includes('Network Error');
  }
  
  return false;
}

/**
 * Check if an error is retryable
 */
export function isRetryableError(error: unknown): boolean {
  const appError = parseError(error);
  return appError.retryable;
}

/**
 * Get retry delay based on attempt number (exponential backoff)
 */
export function getRetryDelay(attempt: number, baseDelay: number = 1000): number {
  return Math.min(baseDelay * Math.pow(2, attempt - 1), 30000); // Max 30 seconds
}

/**
 * Log error for debugging and monitoring
 */
export function logError(error: AppError, context?: string) {
  const logData = {
    ...error,
    context,
    userAgent: navigator.userAgent,
    url: window.location.href
  };

  console.error('Application Error:', logData);

  // In production, you might want to send this to an error tracking service
  if (process.env.NODE_ENV === 'production') {
    // Example: Send to error tracking service
    // errorTrackingService.captureError(logData);
  }
}