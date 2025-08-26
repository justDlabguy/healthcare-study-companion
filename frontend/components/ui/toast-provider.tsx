'use client'

import * as React from 'react'
import { Toast, toastVariants } from './toast'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastType = {
  id: string
  title: string
  description?: string
  variant?: 'default' | 'destructive'
}

type ToastContextType = {
  toasts: ToastType[]
  addToast: (toast: Omit<ToastType, 'id'>) => void
  removeToast: (id: string) => void
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined)

export function useToast() {
  const context = React.useContext(ToastContext)
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastType[]>([])

  const addToast = React.useCallback(({ title, description, variant = 'default' }: Omit<ToastType, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((currentToasts) => [...currentToasts, { id, title, description, variant }])
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setToasts((currentToasts) => currentToasts.filter((toast) => toast.id !== id))
    }, 5000)
  }, [])

  const removeToast = React.useCallback((id: string) => {
    setToasts((currentToasts) => currentToasts.filter((toast) => toast.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <div className="fixed top-0 right-0 z-50 flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]">
        {toasts.map(({ id, title, description, variant }) => (
          <Toast key={id} variant={variant} className="mb-2">
            <div className="grid gap-1">
              {title && <div className="font-semibold">{title}</div>}
              {description && <div className="text-sm opacity-90">{description}</div>}
            </div>
            <button
              onClick={() => removeToast(id)}
              className="absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none group-hover:opacity-100"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </button>
          </Toast>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
