"use client";

import * as React from "react";

interface Toast {
  id: string;
  title?: string;
  description?: string;
  action?: React.ReactNode;
  variant?: "default" | "destructive";
  duration?: number;
  dismissible?: boolean;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => string;
  removeToast: (id: string) => void;
  removeAllToasts: () => void;
}

export const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = React.useContext(ToastContext);
  
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }

  const toast = React.useCallback(
    (props: Omit<Toast, "id">) => {
      return context.addToast(props);
    },
    [context]
  );

  return {
    toast,
    toasts: context.toasts,
    dismiss: context.removeToast,
    dismissAll: context.removeAllToasts,
  };
}