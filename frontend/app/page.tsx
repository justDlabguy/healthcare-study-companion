'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.push('/dashboard');
      } else {
        router.push('/auth/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <main className="py-10 text-center">
        <h1 className="text-2xl font-semibold">Healthcare Study Companion</h1>
        <p className="mt-2 text-gray-600">Loading...</p>
      </main>
    );
  }

  // This will briefly show before redirect
  return (
    <main className="py-10">
      <h1 className="text-2xl font-semibold">Healthcare Study Companion</h1>
      <p className="mt-2 text-gray-600">Redirecting...</p>
    </main>
  );
}
