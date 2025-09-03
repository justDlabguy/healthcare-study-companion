"use client";

import React, { useState, useEffect } from "react";
import { AlertTriangle, CheckCircle, Info, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "default" | "destructive" | "warning" | "success";
  loading?: boolean;
  showIcon?: boolean;
}

export function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default",
  loading = false,
  showIcon = true,
}: ConfirmationDialogProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
      const timer = setTimeout(() => setIsVisible(false), 150);
      return () => clearTimeout(timer);
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !loading) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      return () => document.removeEventListener("keydown", handleEscape);
    }
  }, [isOpen, loading, onClose]);

  const handleConfirm = () => {
    if (!loading) {
      onConfirm();
    }
  };

  const handleCancel = () => {
    if (!loading) {
      onClose();
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "destructive":
        return {
          icon: AlertTriangle,
          iconColor: "text-red-500",
          confirmButton: "bg-red-600 hover:bg-red-700 text-white",
        };
      case "warning":
        return {
          icon: AlertTriangle,
          iconColor: "text-yellow-500",
          confirmButton: "bg-yellow-600 hover:bg-yellow-700 text-white",
        };
      case "success":
        return {
          icon: CheckCircle,
          iconColor: "text-green-500",
          confirmButton: "bg-green-600 hover:bg-green-700 text-white",
        };
      default:
        return {
          icon: Info,
          iconColor: "text-blue-500",
          confirmButton: "bg-blue-600 hover:bg-blue-700 text-white",
        };
    }
  };

  const variantStyles = getVariantStyles();
  const IconComponent = variantStyles.icon;

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        "fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm transition-opacity duration-150",
        isOpen ? "opacity-100" : "opacity-0"
      )}
      onClick={(e) => {
        if (e.target === e.currentTarget && !loading) {
          onClose();
        }
      }}
    >
      <div
        className={cn(
          "bg-white rounded-xl shadow-lg max-w-md w-full transform transition-all duration-150",
          isOpen ? "scale-100 opacity-100" : "scale-95 opacity-0"
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        aria-describedby="dialog-description"
      >
        {/* Header */}
        <div className="flex items-start gap-4 p-6 pb-4">
          {showIcon && (
            <div className="flex-shrink-0">
              <IconComponent
                className={cn("h-6 w-6", variantStyles.iconColor)}
              />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h2
              id="dialog-title"
              className="text-lg font-semibold text-slate-900 mb-2"
            >
              {title}
            </h2>
            <p
              id="dialog-description"
              className="text-sm text-slate-600 leading-relaxed"
            >
              {message}
            </p>
          </div>
          {!loading && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="flex-shrink-0 h-8 w-8 p-0 text-slate-400 hover:text-slate-600"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col-reverse sm:flex-row gap-3 p-6 pt-2 border-t border-slate-100">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={loading}
            className="flex-1 sm:flex-initial"
          >
            {cancelText}
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={loading}
            className={cn(
              "flex-1 sm:flex-initial",
              variantStyles.confirmButton,
              loading && "opacity-50 cursor-not-allowed"
            )}
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Processing...</span>
              </div>
            ) : (
              confirmText
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// Hook for using confirmation dialogs
export function useConfirmationDialog() {
  const [dialog, setDialog] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    variant?: "default" | "destructive" | "warning" | "success";
    onConfirm: () => void;
    loading?: boolean;
  } | null>(null);

  const showConfirmation = (options: {
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    variant?: "default" | "destructive" | "warning" | "success";
    onConfirm: () => void;
  }) => {
    setDialog({
      isOpen: true,
      loading: false,
      ...options,
    });
  };

  const closeDialog = () => {
    setDialog(null);
  };

  const setLoading = (loading: boolean) => {
    if (dialog) {
      setDialog({ ...dialog, loading });
    }
  };

  const DialogComponent = dialog ? (
    <ConfirmationDialog
      isOpen={dialog.isOpen}
      onClose={closeDialog}
      onConfirm={dialog.onConfirm}
      title={dialog.title}
      message={dialog.message}
      confirmText={dialog.confirmText}
      cancelText={dialog.cancelText}
      variant={dialog.variant}
      loading={dialog.loading}
    />
  ) : null;

  return {
    showConfirmation,
    closeDialog,
    setLoading,
    DialogComponent,
  };
}

export default ConfirmationDialog;
