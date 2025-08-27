"use client";

import React, { useState } from "react";
import { testApiConnectivity } from "@/lib/api";

interface CorsDebugPanelProps {
  isVisible?: boolean;
  onClose?: () => void;
}

export const CorsDebugPanel: React.FC<CorsDebugPanelProps> = ({
  isVisible = false,
  onClose,
}) => {
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
    debugInfo: Record<string, unknown>;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const runConnectivityTest = async () => {
    setIsLoading(true);
    try {
      const result = await testApiConnectivity();
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        message: "Test failed to execute",
        debugInfo: {
          error: error instanceof Error ? error.message : "Unknown error",
        },
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl max-h-[80vh] overflow-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">CORS Debug Panel</h2>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          )}
        </div>

        <div className="space-y-4">
          <div>
            <button
              onClick={runConnectivityTest}
              disabled={isLoading}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {isLoading ? "Testing..." : "Test API Connectivity"}
            </button>
          </div>

          {testResult && (
            <div className="border rounded p-4">
              <div
                className={`font-semibold ${
                  testResult.success ? "text-green-600" : "text-red-600"
                }`}
              >
                {testResult.success ? "✅" : "❌"} {testResult.message}
              </div>

              <details className="mt-2">
                <summary className="cursor-pointer text-sm text-gray-600">
                  Debug Information
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">
                  {JSON.stringify(testResult.debugInfo, null, 2)}
                </pre>
              </details>

              {!testResult.success && testResult.debugInfo.suggestions && (
                <div className="mt-3">
                  <div className="text-sm font-medium text-gray-700">
                    Suggestions:
                  </div>
                  <ul className="text-sm text-gray-600 list-disc list-inside">
                    {testResult.debugInfo.suggestions.map(
                      (suggestion: string, index: number) => (
                        <li key={index}>{suggestion}</li>
                      )
                    )}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="text-sm text-gray-600">
            <p>This panel helps diagnose CORS and API connectivity issues.</p>
            <p>Check the browser console for detailed error logs.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CorsDebugPanel;
