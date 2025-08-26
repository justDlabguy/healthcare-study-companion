"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { TopicsList } from "@/components/topics/topics-list";

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="py-10 text-center">
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen">
      {/* Welcome message */}
      <div className="mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600">
              Welcome back, {user?.full_name}!
            </p>
          </div>
          
          {/* Quick stats on larger screens */}
          <div className="hidden sm:flex items-center space-x-4 text-sm text-gray-500">
            <div className="text-center">
              <div className="font-semibold text-gray-900">Study Topics</div>
              <div>Organize your materials</div>
            </div>
          </div>
        </div>
      </div>

      {/* Topics List */}
      <TopicsList />
    </div>
  );
}
