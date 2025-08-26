"use client";

import React, { useState, useCallback, useMemo, useRef } from "react";
import { ToastContext } from "@/components/ui/use-toast";
import { Toaster } from "@/components/ui/toaster";

interface Toast {
  id: string;
  title?: string;
  description?: string;
  action?: React.ReactNode;
  variant?: "default" | "destructive";
  duration?: number;
  dismissible?: boolean;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timersRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  const addToast = useCallback((toast: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substring(2, 9);
    const duration = toast.duration ?? 5000; // Default 5 seconds
    const dismissible = toast.dismissible ?? true; // Default dismissible
    
    const newToast: Toast = { 
      ...toast, 
      id, 
      duration, 
      dismissible 
    };
    
    setToasts((currentToasts) => [...currentToasts, newToast]);
    
    // Auto-dismiss after duration (if duration > 0)
    if (duration > 0) {
      const timer = setTimeout(() => {
        removeToast(id);
      }, duration);
      
      timersRef.current.set(id, timer);
    }
    
    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    // Clear the timer if it exists
    const timer = timersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timersRef.current.delete(id);
    }
    
    setToasts((currentToasts) => currentToasts.filter((toast) => toast.id !== id));
  }, []);

  const removeAllToasts = useCallback(() => {
    // Clear all timers
    timersRef.current.forEach((timer) => clearTimeout(timer));
    timersRef.current.clear();
    
    setToasts([]);
  }, []);

  // Cleanup timers on unmount
  React.useEffect(() => {
    return () => {
      timersRef.current.forEach((timer) => clearTimeout(timer));
      timersRef.current.clear();
    };
  }, []);

  const contextValue = useMemo(
    () => ({
      toasts,
      addToast,
      removeToast,
      removeAllToasts,
    }),
    [toasts, addToast, removeToast, removeAllToasts]
  );

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <Toaster />
    </ToastContext.Provider>
  );
}
