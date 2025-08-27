"use client";

import React, { Component, ReactNode } from "react";
import { CorsDebugPanel } from "@/components/debug/cors-debug-panel";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  showDebugPanel: boolean;
}

export class CorsErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, showDebugPanel: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Check if this is a CORS-related error
    const isCorsError =
      error.name === "CorsError" ||
      error.message.toLowerCase().includes("cors") ||
      error.message.toLowerCase().includes("network error");

    return {
      hasError: isCorsError,
      error: isCorsError ? error : null,
      showDebugPanel: false,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log CORS errors with additional context
    if (this.state.hasError) {
      console.error("CORS Error caught by boundary:", error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center mb-4">
            <div className="text-red-600 text-xl mr-2">🚨</div>
            <h2 className="text-lg font-semibold text-red-800">
              Connection Error
            </h2>
          </div>

          <p className="text-red-700 mb-4">
            Unable to connect to the API server. This is typically a CORS
            configuration issue.
          </p>

          <div className="space-y-2 mb-4">
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 mr-2"
            >
              Retry
            </button>

            <button
              onClick={() => this.setState({ showDebugPanel: true })}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
            >
              Debug Info
            </button>
          </div>

          <details className="text-sm">
            <summary className="cursor-pointer text-red-600 font-medium">
              Technical Details
            </summary>
            <pre className="mt-2 p-2 bg-red-100 rounded text-xs overflow-auto">
              {this.state.error.message}
            </pre>
          </details>

          <CorsDebugPanel
            isVisible={this.state.showDebugPanel}
            onClose={() => this.setState({ showDebugPanel: false })}
          />
        </div>
      );
    }

    return this.props.children;
  }
}

export default CorsErrorBoundary;
