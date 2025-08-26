import { AxiosError } from 'axios';

export interface CorsErrorInfo {
  isCorsError: boolean;
  suggestedFix?: string;
  technicalDetails?: string;
}

/**
 * Detect if an error is likely a CORS error
 */
export function detectCorsError(error: unknown): CorsErrorInfo {
  // Handle Axios errors
  if (error instanceof AxiosError) {
    // Network error with no response usually indicates CORS
    if (error.code === 'ERR_NETWORK' && !error.response) {
      return {
        isCorsError: true,
        suggestedFix: 'The server may not be configured to allow requests from this domain. Please check the server CORS settings.',
        technicalDetails: `Network error without response. This typically indicates a CORS preflight failure or the server is not accessible.`
      };
    }

    // CORS preflight failures
    if (error.response?.status === 0 || error.response?.status === undefined) {
      return {
        isCorsError: true,
        suggestedFix: 'Unable to connect to the server. This may be a CORS issue or the server may be down.',
        technicalDetails: 'Response status is 0 or undefined, indicating a failed preflight request.'
      };
    }

    // Some browsers return 404 for CORS failures
    if (error.response?.status === 404 && error.config?.url?.includes('http')) {
      const url = new URL(error.config.url);
      const currentOrigin = window.location.origin;
      
      if (url.origin !== currentOrigin) {
        return {
          isCorsError: true,
          suggestedFix: `Cross-origin request to ${url.origin} failed. The server may not allow requests from ${currentOrigin}.`,
          technicalDetails: `Cross-origin request returned 404. This may indicate CORS restrictions.`
        };
      }
    }
  }

  // Handle generic errors
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    
    if (message.includes('cors') || 
        message.includes('cross-origin') || 
        message.includes('access-control-allow-origin')) {
      return {
        isCorsError: true,
        suggestedFix: 'The server is not configured to allow requests from this domain.',
        technicalDetails: error.message
      };
    }

    if (message.includes('network error') || message.includes('failed to fetch')) {
      return {
        isCorsError: true,
        suggestedFix: 'Network request failed. This may be due to CORS restrictions or server unavailability.',
        technicalDetails: error.message
      };
    }
  }

  return { isCorsError: false };
}

/**
 * Get user-friendly CORS error message
 */
export function getCorsErrorMessage(error: unknown): string {
  const corsInfo = detectCorsError(error);
  
  if (!corsInfo.isCorsError) {
    return 'An unexpected error occurred.';
  }

  return corsInfo.suggestedFix || 'Connection to server failed due to CORS restrictions.';
}

/**
 * Check if the current environment might have CORS issues
 */
export function checkCorsConfiguration(): {
  hasIssues: boolean;
  issues: string[];
  suggestions: string[];
} {
  const issues: string[] = [];
  const suggestions: string[] = [];

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL;
  const currentOrigin = typeof window !== 'undefined' ? window.location.origin : '';

  // Check if API URL is configured
  if (!apiUrl) {
    issues.push('API URL is not configured');
    suggestions.push('Set NEXT_PUBLIC_API_URL environment variable');
  } else {
    try {
      const apiOrigin = new URL(apiUrl).origin;
      
      // Check if it's a cross-origin request
      if (currentOrigin && apiOrigin !== currentOrigin) {
        issues.push(`Cross-origin request detected: ${currentOrigin} → ${apiOrigin}`);
        suggestions.push('Ensure the backend server includes proper CORS headers');
        suggestions.push(`Add ${currentOrigin} to the server's allowed origins`);
      }

      // Check for localhost/production mismatches
      if (currentOrigin.includes('localhost') && !apiUrl.includes('localhost')) {
        issues.push('Development frontend connecting to production backend');
        suggestions.push('Use a local backend for development or ensure CORS is configured for localhost');
      }

      if (!currentOrigin.includes('localhost') && apiUrl.includes('localhost')) {
        issues.push('Production frontend trying to connect to localhost backend');
        suggestions.push('Update NEXT_PUBLIC_API_URL to point to the production backend');
      }
    } catch (e) {
      issues.push('Invalid API URL format');
      suggestions.push('Check that NEXT_PUBLIC_API_URL is a valid URL');
    }
  }

  // Check for development vs production environment mismatches
  if (typeof window !== 'undefined') {
    const isHttps = window.location.protocol === 'https:';
    const isLocalhost = window.location.hostname === 'localhost';

    if (apiUrl && !isLocalhost) {
      try {
        const apiProtocol = new URL(apiUrl).protocol;
        if (isHttps && apiProtocol === 'http:') {
          issues.push('HTTPS frontend trying to connect to HTTP backend');
          suggestions.push('Use HTTPS for the backend or serve frontend over HTTP in development');
        }
      } catch (e) {
        // URL parsing error already handled above
      }
    }
  }

  return {
    hasIssues: issues.length > 0,
    issues,
    suggestions
  };
}

/**
 * Test CORS configuration by making a simple request
 */
export async function testCorsConfiguration(apiUrl?: string): Promise<{
  success: boolean;
  error?: string;
  corsInfo?: CorsErrorInfo;
}> {
  const testUrl = apiUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  try {
    // Try a simple GET request to test CORS
    const response = await fetch(`${testUrl}/health`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      return { success: true };
    } else {
      return {
        success: false,
        error: `Server responded with status ${response.status}`
      };
    }
  } catch (error) {
    const corsInfo = detectCorsError(error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      corsInfo
    };
  }
}

/**
 * Get CORS troubleshooting steps
 */
export function getCorsTroubleshootingSteps(): string[] {
  return [
    '1. Check that NEXT_PUBLIC_API_URL is set correctly in your environment variables',
    '2. Verify the backend server is running and accessible',
    '3. Ensure the backend includes proper CORS headers (Access-Control-Allow-Origin, etc.)',
    '4. Check that the frontend domain is included in the backend\'s allowed origins',
    '5. For development: Make sure both frontend and backend are using the same protocol (HTTP/HTTPS)',
    '6. Try accessing the API directly in your browser to test connectivity',
    '7. Check browser developer tools Network tab for detailed error information',
    '8. Verify firewall and network settings are not blocking the requests'
  ];
}