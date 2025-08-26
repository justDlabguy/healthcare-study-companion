'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/components/ui/button';
import { Menu, BookOpen, User, LogOut } from 'lucide-react';

interface NavbarProps {
  onToggleSidebar?: () => void;
  showSidebarToggle?: boolean;
}

export function Navbar({ onToggleSidebar, showSidebarToggle = false }: NavbarProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
    router.push('/auth/login');
    setShowUserMenu(false);
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 safe-area-inset">
      <div className="max-w-7xl mx-auto mobile-padding">
        <div className="flex justify-between items-center h-16">
          {/* Left side */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            {/* Sidebar toggle (mobile) */}
            {showSidebarToggle && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleSidebar}
                className="lg:hidden touch-target"
                aria-label="Toggle sidebar"
              >
                <Menu className="h-5 w-5" />
              </Button>
            )}
            
            {/* Logo and brand */}
            <Link href="/dashboard" className="flex items-center space-x-2 touch-target">
              <BookOpen className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
              <span className="text-lg sm:text-xl font-bold text-gray-900 hidden sm:block">
                Study Companion
              </span>
              <span className="text-base font-bold text-gray-900 sm:hidden">
                SC
              </span>
            </Link>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            {isAuthenticated ? (
              <div className="relative">
                {/* User menu button */}
                <Button
                  variant="ghost"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 touch-target"
                  aria-label="User menu"
                >
                  <User className="h-4 w-4 sm:h-5 sm:w-5" />
                  <span className="hidden md:block text-sm truncate max-w-32">
                    {user?.full_name}
                  </span>
                </Button>

                {/* User dropdown menu */}
                {showUserMenu && (
                  <>
                    {/* Mobile backdrop */}
                    <div 
                      className="fixed inset-0 z-40 sm:hidden" 
                      onClick={() => setShowUserMenu(false)}
                    />
                    <div className="absolute right-0 mt-2 w-56 sm:w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                      <div className="py-1">
                        <div className="px-4 py-3 text-sm text-gray-700 border-b border-gray-100">
                          <div className="font-medium truncate">{user?.full_name}</div>
                          <div className="text-gray-500 text-xs truncate">{user?.email}</div>
                        </div>
                        
                        <Link
                          href="/dashboard"
                          className="block px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 touch-target"
                          onClick={() => setShowUserMenu(false)}
                        >
                          Dashboard
                        </Link>
                        
                        <button
                          onClick={handleLogout}
                          className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2 touch-target"
                        >
                          <LogOut className="h-4 w-4" />
                          <span>Sign Out</span>
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link href="/auth/login">
                  <Button variant="ghost" size="sm" className="touch-target">
                    <span className="hidden xs:inline">Sign In</span>
                    <span className="xs:hidden">In</span>
                  </Button>
                </Link>
                <Link href="/auth/signup">
                  <Button size="sm" className="touch-target">
                    <span className="hidden xs:inline">Sign Up</span>
                    <span className="xs:hidden">Up</span>
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Click outside to close user menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </nav>
  );
}