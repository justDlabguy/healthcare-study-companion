"use client"

import * as React from "react"
import { X } from "lucide-react"
import { useToast } from "./use-toast"
import { cn } from "@/lib/utils"
import { Button } from "./button"

const toastVariants = {
  default: "bg-background text-foreground border border-border",
  destructive: "bg-destructive text-destructive-foreground border-destructive/50",
}

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <div className="fixed top-4 right-4 z-[100] flex max-h-screen w-full flex-col space-y-2 p-4 sm:bottom-4 sm:right-4 sm:top-auto md:max-w-[420px] safe-area-inset">
      {toasts.map(({ id, title, description, action, variant = "default", dismissible = true, ...props }) => {
        return (
          <div
            key={id}
            className={cn(
              "group pointer-events-auto relative flex w-full items-start justify-between space-x-4 overflow-hidden rounded-lg border p-4 pr-8 shadow-lg transition-all duration-300 ease-in-out animate-in slide-in-from-top-2",
              toastVariants[variant],
              "hover:shadow-xl"
            )}
            {...props}
          >
            <div className="grid gap-1 flex-1 min-w-0">
              {title && (
                <div className="text-sm font-semibold leading-none tracking-tight">
                  {title}
                </div>
              )}
              {description && (
                <div className="text-sm opacity-90 leading-relaxed">
                  {description}
                </div>
              )}
            </div>
            
            {action && (
              <div className="flex-shrink-0">
                {action}
              </div>
            )}
            
            {dismissible && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1 h-6 w-6 rounded-md opacity-0 transition-opacity hover:opacity-100 focus:opacity-100 group-hover:opacity-100 touch-target"
                onClick={() => dismiss(id)}
                aria-label="Close notification"
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
        )
      })}
      
      {/* Clear all button when there are multiple toasts */}
      {toasts.length > 1 && (
        <div className="flex justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={() => toasts.forEach(toast => dismiss(toast.id))}
            className="text-xs opacity-75 hover:opacity-100"
          >
            Clear all
          </Button>
        </div>
      )}
    </div>
  )
}
