"use client";

import { useCallback, useState } from "react";
import { testApiConnectivity } from "@/lib/api";

interface CorsErrorState {
  hasCorsError: boolean;
  errorMessage: string;
  debugInfo: any;
  isRetrying: boolean;
}

export const useCorsErrorHandler = () => {
  const [corsErrorState, setCorsErrorState] = useState<CorsErrorState>({
    hasCorsError: false,
    errorMessage: "",
    debugInfo: null,
    isRetrying: false,
  });

  const handleError = useCallback((error: any) => {
    // Check if this is a CORS error
    if (
      error.name === "CorsError" ||
      (error.originalError && isCorsError(error.originalError))
    ) {
      setCorsErrorState({
        hasCorsError: true,
        errorMessage: error.message,
        debugInfo: error.debugInfo,
        isRetrying: false,
      });
      return true; // Indicates this was a CORS error
    }
    return false; // Not a CORS error
  }, []);

  const retryConnection = useCallback(async () => {
    setCorsErrorState((prev) => ({ ...prev, isRetrying: true }));

    try {
      const result = await testApiConnectivity();
      if (result.success) {
        setCorsErrorState({
          hasCorsError: false,
          errorMessage: "",
          debugInfo: null,
          isRetrying: false,
        });
        return true;
      } else {
        setCorsErrorState((prev) => ({
          ...prev,
          errorMessage: result.message,
          debugInfo: result.debugInfo,
          isRetrying: false,
        }));
        return false;
      }
    } catch (error) {
      setCorsErrorState((prev) => ({
        ...prev,
        isRetrying: false,
      }));
      return false;
    }
  }, []);

  const clearError = useCallback(() => {
    setCorsErrorState({
      hasCorsError: false,
      errorMessage: "",
      debugInfo: null,
      isRetrying: false,
    });
  }, []);

  return {
    corsErrorState,
    handleError,
    retryConnection,
    clearError,
  };
};

// Helper function to detect CORS errors (duplicated here for the hook)
function isCorsError(error: any): boolean {
  if (error.code === "ERR_NETWORK" && !error.response) {
    return true;
  }

  const corsIndicators = [
    "cors",
    "cross-origin",
    "preflight",
    "access-control-allow-origin",
    "network error",
  ];

  const errorMessage = (error.message || "").toLowerCase();
  return corsIndicators.some((indicator) => errorMessage.includes(indicator));
}

export default useCorsErrorHandler;
