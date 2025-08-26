'use client';

import './globals.css';
import React from 'react';
import { AuthProvider } from '../contexts/auth-context';
import { ToastProvider } from '../components/providers/toast-provider';
import { Toaster } from '../components/ui/toaster';
import { AppLayout } from '../components/navigation';
import ErrorBoundary from '../components/error-boundary';
import { PerformanceMonitor } from '../components/dev/performance-monitor';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <ErrorBoundary 
          level="page" 
          showErrorDetails={process.env.NODE_ENV === 'development'}
          onError={(error, errorInfo) => {
            console.error('Root layout error:', error, errorInfo);
            // In production, you might want to send this to an error tracking service
          }}
        >
          <ToastProvider>
            <AuthProvider>
              <ErrorBoundary level="section">
                <AppLayout>
                  <ErrorBoundary level="component">
                    {children}
                  </ErrorBoundary>
                </AppLayout>
              </ErrorBoundary>
            </AuthProvider>
            <Toaster />
            <PerformanceMonitor />
          </ToastProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}
