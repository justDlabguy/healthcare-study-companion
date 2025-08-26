'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/auth-context';
import { useErrorToast } from '@/hooks/use-error-toast';
import { useAsyncOperation } from '@/hooks/use-async-operation';
import ErrorBoundary from '@/components/error-boundary';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState('');
  
  const { login } = useAuth();
  const router = useRouter();
  const { showError, showSuccess } = useErrorToast();

  const loginOperation = async () => {
    // Basic validation
    if (!email || !password) {
      setValidationError('Please fill in all fields');
      throw new Error('Please fill in all fields');
    }

    if (!email.includes('@')) {
      setValidationError('Please enter a valid email address');
      throw new Error('Please enter a valid email address');
    }

    setValidationError('');
    
    await login(email, password);
    showSuccess('Login successful! Redirecting to dashboard...');
    router.push('/dashboard' as any);
  };

  const { execute: handleLogin, isLoading, error } = useAsyncOperation(
    loginOperation,
    {
      enableRetry: true,
      showErrorToast: true,
      retryOptions: {
        maxAttempts: 3,
        baseDelay: 1000
      }
    }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleLogin();
  };

  return (
    <ErrorBoundary level="page">
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">Study Companion</h1>
            <p className="mt-2 text-gray-600">Sign in to your account</p>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Sign In</CardTitle>
              <CardDescription>
                Enter your email and password to access your account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {validationError && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                    {validationError}
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    required
                    disabled={isLoading}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                    disabled={isLoading}
                  />
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full" 
                  disabled={isLoading}
                >
                  {isLoading ? 'Signing in...' : 'Sign In'}
                </Button>
              </form>
              
              <div className="mt-6 text-center space-y-2">
                <Link 
                  href={"/auth/forgot-password" as any}
                  className="text-sm text-blue-600 hover:text-blue-500"
                >
                  Forgot your password?
                </Link>
                <div className="text-sm text-gray-600">
                  Don't have an account?{' '}
                  <Link 
                    href={"/auth/signup" as any}
                    className="text-blue-600 hover:text-blue-500 font-medium"
                  >
                    Sign up
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ErrorBoundary>
  );
}