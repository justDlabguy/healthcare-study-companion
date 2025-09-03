"use client";

import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface MobileOptimizedProps {
  children: React.ReactNode;
  className?: string;
}

// Hook to detect mobile device
export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkIsMobile();
    window.addEventListener("resize", checkIsMobile);
    return () => window.removeEventListener("resize", checkIsMobile);
  }, []);

  return isMobile;
}

// Hook to detect touch device
export function useIsTouchDevice() {
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    setIsTouchDevice("ontouchstart" in window || navigator.maxTouchPoints > 0);
  }, []);

  return isTouchDevice;
}

// Mobile-optimized container
export function MobileOptimized({ children, className }: MobileOptimizedProps) {
  const isMobile = useIsMobile();
  const isTouchDevice = useIsTouchDevice();

  return (
    <div
      className={cn(
        "w-full",
        {
          // Mobile-specific optimizations
          "touch-pan-y": isTouchDevice,
          "overscroll-behavior-y-contain": isMobile,
        },
        className
      )}
      style={{
        // Prevent zoom on double tap
        touchAction: isTouchDevice ? "manipulation" : "auto",
        // Improve scrolling on iOS
        WebkitOverflowScrolling: "touch",
      }}
    >
      {children}
    </div>
  );
}

// Mobile-optimized button
interface MobileButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
}

export function MobileButton({
  children,
  variant = "primary",
  size = "md",
  fullWidth = false,
  className,
  ...props
}: MobileButtonProps) {
  const isTouchDevice = useIsTouchDevice();

  const baseClasses = cn(
    "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200",
    "focus:outline-none focus:ring-2 focus:ring-offset-2",
    "disabled:opacity-50 disabled:cursor-not-allowed",
    {
      // Touch-friendly sizing
      "min-h-[44px] px-4 py-3 text-sm": size === "sm" && isTouchDevice,
      "min-h-[48px] px-6 py-3 text-base": size === "md" && isTouchDevice,
      "min-h-[52px] px-8 py-4 text-lg": size === "lg" && isTouchDevice,
      // Desktop sizing
      "h-9 px-3 py-2 text-sm": size === "sm" && !isTouchDevice,
      "h-10 px-4 py-2 text-sm": size === "md" && !isTouchDevice,
      "h-11 px-8 py-2 text-base": size === "lg" && !isTouchDevice,
      // Full width
      "w-full": fullWidth,
    }
  );

  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary:
      "bg-slate-200 text-slate-900 hover:bg-slate-300 focus:ring-slate-500",
    ghost:
      "bg-transparent text-slate-700 hover:bg-slate-100 focus:ring-slate-500",
  };

  return (
    <button
      className={cn(baseClasses, variantClasses[variant], className)}
      {...props}
    >
      {children}
    </button>
  );
}

// Mobile-optimized input
interface MobileInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

export function MobileInput({
  label,
  error,
  fullWidth = true,
  className,
  ...props
}: MobileInputProps) {
  const isTouchDevice = useIsTouchDevice();

  return (
    <div className={cn("space-y-2", { "w-full": fullWidth })}>
      {label && (
        <label className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <input
        className={cn(
          "block rounded-lg border border-slate-300 bg-white px-4 py-3",
          "focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none",
          "disabled:bg-slate-50 disabled:text-slate-500",
          {
            // Touch-friendly sizing
            "min-h-[48px] text-base": isTouchDevice,
            "h-10 text-sm": !isTouchDevice,
            "w-full": fullWidth,
            "border-red-300 focus:border-red-500 focus:ring-red-500/20": error,
          },
          className
        )}
        {...props}
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}

// Mobile-optimized card
interface MobileCardProps {
  children: React.ReactNode;
  className?: string;
  padding?: "sm" | "md" | "lg";
  interactive?: boolean;
  onClick?: () => void;
}

export function MobileCard({
  children,
  className,
  padding = "md",
  interactive = false,
  onClick,
}: MobileCardProps) {
  const isTouchDevice = useIsTouchDevice();

  const paddingClasses = {
    sm: "p-3",
    md: isTouchDevice ? "p-4" : "p-4",
    lg: isTouchDevice ? "p-6" : "p-6",
  };

  return (
    <div
      className={cn(
        "bg-white rounded-lg border border-slate-200 shadow-sm",
        paddingClasses[padding],
        {
          "cursor-pointer hover:shadow-md transition-shadow duration-200":
            interactive,
          "active:scale-[0.98] transition-transform duration-100":
            interactive && isTouchDevice,
        },
        className
      )}
      onClick={onClick}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
    >
      {children}
    </div>
  );
}

// Mobile-optimized modal
interface MobileModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  fullScreen?: boolean;
}

export function MobileModal({
  isOpen,
  onClose,
  children,
  title,
  fullScreen = false,
}: MobileModalProps) {
  const isMobile = useIsMobile();

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className={cn("relative bg-white shadow-xl", {
          // Mobile: slide up from bottom, full screen
          "w-full h-full sm:h-auto sm:w-auto sm:max-w-lg sm:rounded-lg":
            fullScreen || isMobile,
          "rounded-t-xl sm:rounded-lg": !fullScreen && isMobile,
          "max-w-lg w-full rounded-lg": !isMobile,
        })}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between p-4 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        )}

        {/* Content */}
        <div
          className={cn("overflow-y-auto", {
            "flex-1": fullScreen || isMobile,
            "max-h-[80vh]": !fullScreen && !isMobile,
          })}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

// Mobile-optimized navigation
interface MobileNavProps {
  items: Array<{
    label: string;
    href: string;
    icon?: React.ReactNode;
    active?: boolean;
  }>;
  className?: string;
}

export function MobileNav({ items, className }: MobileNavProps) {
  return (
    <nav className={cn("flex overflow-x-auto pb-2", className)}>
      <div className="flex space-x-1 min-w-max px-4">
        {items.map((item, index) => (
          <a
            key={index}
            href={item.href}
            className={cn(
              "flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors",
              {
                "bg-blue-100 text-blue-700": item.active,
                "text-slate-600 hover:text-slate-900 hover:bg-slate-100":
                  !item.active,
              }
            )}
          >
            {item.icon}
            <span>{item.label}</span>
          </a>
        ))}
      </div>
    </nav>
  );
}

export default MobileOptimized;
