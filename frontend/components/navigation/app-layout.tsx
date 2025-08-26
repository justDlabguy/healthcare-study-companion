'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Navbar } from './navbar';
import { Sidebar } from './sidebar';
import { Breadcrumb, generateBreadcrumbs } from './breadcrumb';
import { topicsApi, type Topic } from '@/lib/api';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { isAuthenticated } = useAuth();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentTopic, setCurrentTopic] = useState<Topic | null>(null);

  // Extract topic ID from pathname
  const topicId = pathname.match(/\/topics\/(\d+)/)?.[1];

  // Load current topic for breadcrumbs
  useEffect(() => {
    if (topicId && isAuthenticated) {
      loadCurrentTopic(parseInt(topicId));
    } else {
      setCurrentTopic(null);
    }
  }, [topicId, isAuthenticated]);

  const loadCurrentTopic = async (id: number) => {
    try {
      const topic = await topicsApi.getTopic(id);
      setCurrentTopic(topic);
    } catch (error) {
      console.error('Failed to load current topic:', error);
      setCurrentTopic(null);
    }
  };

  const closeSidebar = () => setSidebarOpen(false);
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  // Don't show navigation on auth pages or landing page
  const isAuthPage = pathname.startsWith('/auth');
  const isLandingPage = pathname === '/';
  const showNavigation = isAuthenticated && !isAuthPage && !isLandingPage;

  // Generate breadcrumbs
  const breadcrumbs = generateBreadcrumbs(pathname, currentTopic?.title);

  if (!showNavigation) {
    // Full-screen layout for auth pages and landing
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar 
          onToggleSidebar={toggleSidebar}
          showSidebarToggle={false}
        />
        <main className="min-h-screen safe-area-inset">
          {children}
        </main>
      </div>
    );
  }

  // Authenticated layout with navigation
  return (
    <div className="min-h-screen bg-gray-50 safe-area-inset">
      {/* Navigation bar */}
      <Navbar 
        onToggleSidebar={toggleSidebar}
        showSidebarToggle={true}
      />

      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen}
          onClose={closeSidebar}
        />

        {/* Main content area */}
        <div className="flex-1 min-w-0">
          {/* Breadcrumbs */}
          {breadcrumbs.length > 0 && (
            <div className="mobile-padding py-3 sm:py-4 border-b border-gray-200 bg-white">
              <div className="max-w-6xl mx-auto">
                <Breadcrumb items={breadcrumbs} />
              </div>
            </div>
          )}

          {/* Page content */}
          <main className="mobile-padding py-4 sm:py-6 lg:py-8">
            <div className="max-w-6xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}