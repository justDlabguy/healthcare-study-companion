'use client';

import React from 'react';
import Link from 'next/link';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className = '' }: BreadcrumbProps) {
  return (
    <nav className={`flex items-center space-x-1 text-sm text-gray-500 overflow-x-auto ${className}`} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-1 min-w-0">
        {/* Home link */}
        <li className="flex-shrink-0">
          <Link
            href="/dashboard"
            className="flex items-center text-gray-400 hover:text-gray-600 transition-colors"
          >
            <Home className="h-4 w-4" />
            <span className="sr-only">Dashboard</span>
          </Link>
        </li>

        {/* Breadcrumb items */}
        {items.map((item, index) => (
          <li key={index} className="flex items-center min-w-0">
            <ChevronRight className="h-4 w-4 text-gray-300 mx-1 flex-shrink-0" />
            
            {item.href && !item.current ? (
              <Link
                href={item.href}
                className="text-gray-500 hover:text-gray-700 transition-colors truncate max-w-[150px] sm:max-w-xs"
                title={item.label}
              >
                {item.label}
              </Link>
            ) : (
              <span
                className={`truncate max-w-[150px] sm:max-w-xs ${
                  item.current ? 'text-gray-900 font-medium' : 'text-gray-500'
                }`}
                title={item.label}
              >
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

// Helper function to generate breadcrumbs for common routes
export function generateBreadcrumbs(pathname: string, topicTitle?: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [];

  if (segments.length === 0 || segments[0] === 'dashboard') {
    return [{ label: 'Dashboard', current: true }];
  }

  // Handle topic routes
  if (segments[0] === 'topics' && segments[1]) {
    const topicId = segments[1];
    
    breadcrumbs.push({
      label: 'Topics',
      href: '/dashboard'
    });

    if (topicTitle) {
      breadcrumbs.push({
        label: topicTitle,
        href: `/topics/${topicId}`,
        current: segments.length === 2
      });

      // Handle sub-pages
      if (segments[2]) {
        const subPage = segments[2];
        const subPageLabels: Record<string, string> = {
          'qa': 'Q&A',
          'flashcards': 'Flashcards',
          'documents': 'Documents'
        };

        breadcrumbs.push({
          label: subPageLabels[subPage] || subPage,
          current: true
        });
      }
    } else {
      breadcrumbs.push({
        label: `Topic ${topicId}`,
        current: true
      });
    }
  }

  // Handle auth routes
  else if (segments[0] === 'auth') {
    const authLabels: Record<string, string> = {
      'login': 'Sign In',
      'signup': 'Sign Up',
      'forgot-password': 'Reset Password'
    };

    breadcrumbs.push({
      label: authLabels[segments[1]] || 'Authentication',
      current: true
    });
  }

  // Default case
  else {
    breadcrumbs.push({
      label: segments[segments.length - 1].charAt(0).toUpperCase() + segments[segments.length - 1].slice(1),
      current: true
    });
  }

  return breadcrumbs;
}