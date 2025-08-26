"use client"

import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

export type ToastVariant = "default" | "destructive"

export interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: ToastVariant
  onDismiss?: () => void
  duration?: number
  children?: React.ReactNode
}

const toastVariants = {
  default: "bg-background text-foreground border",
  destructive:
    "bg-destructive text-destructive-foreground border-destructive/50",
}

export function Toast({
  className,
  variant = "default",
  onDismiss,
  children,
  duration = 5000,
  ...props
}: ToastProps) {
  React.useEffect(() => {
    if (duration && onDismiss) {
      const timer = setTimeout(onDismiss, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onDismiss])

  return (
    <div
      className={cn(
        "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all",
        toastVariants[variant],
        className
      )}
      {...props}
    >
      {children}
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
