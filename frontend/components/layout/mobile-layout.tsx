"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import {
  Home,
  BookOpen,
  Brain,
  MessageSquare,
  Search,
  Menu,
  X,
  User,
  Settings,
} from "lucide-react";

interface MobileLayoutProps {
  children: React.ReactNode;
}

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: number;
}

export function MobileLayout({ children }: MobileLayoutProps) {
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const pathname = usePathname();

  // Handle scroll for header styling
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setShowMobileMenu(false);
  }, [pathname]);

  const mainNavItems: NavItem[] = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: <Home className="h-5 w-5" />,
    },
    {
      label: "Topics",
      href: "/topics",
      icon: <BookOpen className="h-5 w-5" />,
    },
    {
      label: "Search",
      href: "/search",
      icon: <Search className="h-5 w-5" />,
    },
  ];

  const quickActions: NavItem[] = [
    {
      label: "Flashcards",
      href: "/flashcards",
      icon: <Brain className="h-4 w-4" />,
    },
    {
      label: "Q&A",
      href: "/qa",
      icon: <MessageSquare className="h-4 w-4" />,
    },
  ];

  const isActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/" || pathname === "/dashboard";
    }
    return pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Mobile Header */}
      <header
        className={cn(
          "sticky top-0 z-40 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 transition-all duration-200",
          {
            "shadow-sm": isScrolled,
          }
        )}
        style={{
          paddingTop: "env(safe-area-inset-top)",
        }}
      >
        <div className="flex h-16 items-center justify-between px-4">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
              <BookOpen className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold text-slate-900">Study</span>
          </Link>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="flex h-10 w-10 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
            aria-label="Toggle menu"
          >
            {showMobileMenu ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Mobile Menu Overlay */}
        {showMobileMenu && (
          <>
            <div
              className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
              onClick={() => setShowMobileMenu(false)}
            />
            <div className="absolute right-0 top-full z-50 w-80 max-w-[calc(100vw-2rem)] bg-white shadow-xl rounded-bl-xl border-l border-b border-slate-200">
              <div className="p-4 space-y-6">
                {/* Main Navigation */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 mb-3">
                    Navigation
                  </h3>
                  <nav className="space-y-1">
                    {mainNavItems.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={cn(
                          "flex items-center space-x-3 px-3 py-3 rounded-lg text-sm font-medium transition-colors",
                          {
                            "bg-blue-50 text-blue-700": isActive(item.href),
                            "text-slate-700 hover:bg-slate-100 hover:text-slate-900":
                              !isActive(item.href),
                          }
                        )}
                      >
                        {item.icon}
                        <span>{item.label}</span>
                        {item.badge && (
                          <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    ))}
                  </nav>
                </div>

                {/* Quick Actions */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 mb-3">
                    Quick Actions
                  </h3>
                  <div className="grid grid-cols-2 gap-2">
                    {quickActions.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        className="flex flex-col items-center space-y-2 p-3 rounded-lg text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors"
                      >
                        {item.icon}
                        <span className="text-xs font-medium">
                          {item.label}
                        </span>
                      </Link>
                    ))}
                  </div>
                </div>

                {/* User Actions */}
                <div className="border-t border-slate-200 pt-4">
                  <div className="space-y-1">
                    <Link
                      href="/settings"
                      className="flex items-center space-x-3 px-3 py-3 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors"
                    >
                      <Settings className="h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                    <Link
                      href="/profile"
                      className="flex items-center space-x-3 px-3 py-3 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors"
                    >
                      <User className="h-4 w-4" />
                      <span>Profile</span>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div
          className="mx-auto max-w-7xl px-4 py-6"
          style={{
            paddingBottom: "calc(env(safe-area-inset-bottom) + 1.5rem)",
          }}
        >
          {children}
        </div>
      </main>

      {/* Bottom Navigation (Mobile) */}
      <nav
        className="fixed bottom-0 left-0 right-0 z-30 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 border-t border-slate-200 md:hidden"
        style={{
          paddingBottom: "env(safe-area-inset-bottom)",
        }}
      >
        <div className="flex items-center justify-around px-2 py-2">
          {mainNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center space-y-1 px-3 py-2 rounded-lg text-xs font-medium transition-colors min-w-0 flex-1",
                {
                  "text-blue-600": isActive(item.href),
                  "text-slate-600 hover:text-slate-900": !isActive(item.href),
                }
              )}
            >
              <div
                className={cn("p-1.5 rounded-lg transition-colors", {
                  "bg-blue-100": isActive(item.href),
                  "hover:bg-slate-100": !isActive(item.href),
                })}
              >
                {item.icon}
              </div>
              <span className="truncate">{item.label}</span>
              {item.badge && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[1.25rem] text-center">
                  {item.badge}
                </span>
              )}
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}

// Mobile-optimized page wrapper
interface MobilePageProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

export function MobilePage({
  children,
  title,
  subtitle,
  action,
  className,
}: MobilePageProps) {
  return (
    <div className={cn("space-y-6", className)}>
      {/* Page Header */}
      {(title || subtitle || action) && (
        <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="min-w-0 flex-1">
            {title && (
              <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="mt-2 text-sm text-slate-600 sm:text-base">
                {subtitle}
              </p>
            )}
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>
      )}

      {/* Page Content */}
      <div>{children}</div>
    </div>
  );
}

export default MobileLayout;
