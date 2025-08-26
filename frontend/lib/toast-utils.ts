import { useToast } from "@/components/ui/use-toast";

// Toast utility functions for common use cases
export function useToastUtils() {
  const { toast, dismiss, dismissAll } = useToast();

  const showSuccess = (title: string, description?: string, duration?: number) => {
    return toast({
      title,
      description,
      variant: "default",
      duration: duration ?? 4000,
      dismissible: true,
    });
  };

  const showError = (title: string, description?: string, duration?: number) => {
    return toast({
      title,
      description,
      variant: "destructive",
      duration: duration ?? 6000, // Errors stay longer
      dismissible: true,
    });
  };

  const showInfo = (title: string, description?: string, duration?: number) => {
    return toast({
      title,
      description,
      variant: "default",
      duration: duration ?? 5000,
      dismissible: true,
    });
  };

  const showPersistent = (title: string, description?: string, variant: "default" | "destructive" = "default") => {
    return toast({
      title,
      description,
      variant,
      duration: 0, // Never auto-dismiss
      dismissible: true,
    });
  };

  const showLoading = (title: string, description?: string) => {
    return toast({
      title,
      description,
      variant: "default",
      duration: 0, // Don't auto-dismiss loading toasts
      dismissible: false, // Can't manually dismiss loading toasts
    });
  };

  const showNetworkError = () => {
    return showError(
      "Connection Error",
      "Unable to connect to the server. Please check your internet connection and try again.",
      8000
    );
  };

  const showValidationError = (message: string) => {
    return showError(
      "Validation Error",
      message,
      5000
    );
  };

  const showServerError = () => {
    return showError(
      "Server Error",
      "Something went wrong on our end. Please try again in a few moments.",
      6000
    );
  };

  return {
    showSuccess,
    showError,
    showInfo,
    showPersistent,
    showLoading,
    showNetworkError,
    showValidationError,
    showServerError,
    dismiss,
    dismissAll,
  };
}

// Hook for handling API errors with toasts
export function useApiErrorToast() {
  const { showError, showNetworkError, showServerError } = useToastUtils();

  const handleApiError = (error: any, customMessage?: string) => {
    console.error('API Error:', error);

    if (!error.response) {
      // Network error
      showNetworkError();
      return;
    }

    const status = error.response.status;
    const data = error.response.data;

    if (status >= 500) {
      showServerError();
    } else if (status === 401) {
      showError(
        "Authentication Required",
        "Your session has expired. Please log in again.",
        6000
      );
    } else if (status === 403) {
      showError(
        "Access Denied",
        "You don't have permission to perform this action.",
        5000
      );
    } else if (status === 404) {
      showError(
        "Not Found",
        customMessage || "The requested resource was not found.",
        5000
      );
    } else if (status === 400) {
      // Validation error
      let message = customMessage || "Please check your input and try again.";
      
      if (data?.detail) {
        if (Array.isArray(data.detail)) {
          message = data.detail.map((err: any) => err.msg || err.message).join(', ');
        } else if (typeof data.detail === 'string') {
          message = data.detail;
        }
      } else if (data?.message) {
        message = data.message;
      }
      
      showError("Validation Error", message, 5000);
    } else {
      // Generic error
      showError(
        "Error",
        customMessage || data?.message || "An unexpected error occurred.",
        5000
      );
    }
  };

  return { handleApiError };
}

// Toast configuration presets
export const TOAST_PRESETS = {
  success: {
    duration: 4000,
    variant: "default" as const,
    dismissible: true,
  },
  error: {
    duration: 6000,
    variant: "destructive" as const,
    dismissible: true,
  },
  info: {
    duration: 5000,
    variant: "default" as const,
    dismissible: true,
  },
  warning: {
    duration: 7000,
    variant: "default" as const,
    dismissible: true,
  },
  loading: {
    duration: 0,
    variant: "default" as const,
    dismissible: false,
  },
  persistent: {
    duration: 0,
    variant: "default" as const,
    dismissible: true,
  },
} as const;