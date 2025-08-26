"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { useErrorToast } from "@/hooks/use-error-toast";
import { useAsyncOperation } from "@/hooks/use-async-operation";
import ErrorBoundary from "@/components/error-boundary";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [validationError, setValidationError] = useState("");

  const { signup } = useAuth();
  const router = useRouter();
  const { showError, showSuccess } = useErrorToast();

  const signupOperation = async () => {
    // Basic validation
    if (!email || !password || !confirmPassword || !fullName) {
      setValidationError("Please fill in all fields");
      throw new Error("Please fill in all fields");
    }

    if (!email.includes("@")) {
      setValidationError("Please enter a valid email address");
      throw new Error("Please enter a valid email address");
    }

    if (password.length < 6) {
      setValidationError("Password must be at least 6 characters long");
      throw new Error("Password must be at least 6 characters long");
    }

    if (password !== confirmPassword) {
      setValidationError("Passwords do not match");
      throw new Error("Passwords do not match");
    }

    setValidationError("");
    
    await signup(email, password, fullName);
    showSuccess("Account created successfully! Redirecting to dashboard...");
    router.push("/dashboard" as any);
  };

  const { execute: handleSignup, isLoading, error } = useAsyncOperation(
    signupOperation,
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
    await handleSignup();
  };

  return (
    <ErrorBoundary level="page">
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">
              Healthcare Study Companion
            </h1>
            <p className="mt-2 text-gray-600">Create your account</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Sign Up</CardTitle>
              <CardDescription>
                Create a new account to start studying
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
                  <Label htmlFor="fullName">Full Name</Label>
                  <Input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Enter your full name"
                    required
                    disabled={isLoading}
                  />
                </div>

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
                  <p className="text-xs text-gray-500">
                    Password must be at least 6 characters long
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    required
                    disabled={isLoading}
                  />
                </div>

                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Creating account..." : "Create Account"}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <div className="text-sm text-gray-600">
                  Already have an account?{" "}
                  <Link
                    href={"/auth/login" as any}
                    className="text-blue-600 hover:text-blue-500 font-medium"
                  >
                    Sign in
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
