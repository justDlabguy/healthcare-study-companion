# CORS Error Handling and Debugging

This document explains the enhanced CORS error handling implemented in the frontend API client.

## Features

### 1. Enhanced CORS Error Detection

The API client now includes sophisticated CORS error detection that identifies:

- Network errors without responses (typical CORS indicator)
- Error messages containing CORS-related keywords
- Preflight request failures

### 2. Detailed Debugging Information

When a CORS error occurs, the system logs comprehensive debugging information:

- Current frontend origin
- API base URL
- Expected CORS origins
- Full request details
- Troubleshooting suggestions

### 3. Consistent Base URL Handling

The API client ensures consistent URL handling by:

- Removing trailing slashes from environment variables
- Preventing double slashes in request URLs
- Using consistent hostname formats (localhost vs 127.0.0.1)

## Usage

### Basic API Calls

The enhanced error handling works automatically with all API calls:

```typescript
import { authApi } from "@/lib/api";

try {
  const user = await authApi.login({ email, password });
  // Handle success
} catch (error) {
  // CORS errors are automatically detected and enhanced
  if (error.name === "CorsError") {
    console.log("CORS issue detected:", error.debugInfo);
  }
}
```

### Using the CORS Error Hook

For React components that need to handle CORS errors gracefully:

```typescript
import { useCorsErrorHandler } from "@/hooks/use-cors-error-handler";

function MyComponent() {
  const { corsErrorState, handleError, retryConnection } =
    useCorsErrorHandler();

  const handleApiCall = async () => {
    try {
      await someApiCall();
    } catch (error) {
      if (handleError(error)) {
        // This was a CORS error, handled by the hook
        return;
      }
      // Handle other types of errors
    }
  };

  if (corsErrorState.hasCorsError) {
    return (
      <div>
        <p>Connection error: {corsErrorState.errorMessage}</p>
        <button onClick={retryConnection}>Retry</button>
      </div>
    );
  }

  return <div>Normal component content</div>;
}
```

### Using the CORS Error Boundary

Wrap components that make API calls with the CORS error boundary:

```typescript
import { CorsErrorBoundary } from "@/components/error/cors-error-boundary";

function App() {
  return (
    <CorsErrorBoundary>
      <ComponentThatMakesApiCalls />
    </CorsErrorBoundary>
  );
}
```

### Testing API Connectivity

Use the built-in connectivity test function:

```typescript
import { testApiConnectivity } from "@/lib/api";

const testConnection = async () => {
  const result = await testApiConnectivity();
  if (result.success) {
    console.log("API is accessible");
  } else {
    console.log("Connection issues:", result.debugInfo);
  }
};
```

### Using the Debug Panel

The CORS debug panel can be used for manual testing:

```typescript
import { CorsDebugPanel } from "@/components/debug/cors-debug-panel";

function DebugPage() {
  const [showPanel, setShowPanel] = useState(false);

  return (
    <div>
      <button onClick={() => setShowPanel(true)}>
        Test CORS Configuration
      </button>
      <CorsDebugPanel
        isVisible={showPanel}
        onClose={() => setShowPanel(false)}
      />
    </div>
  );
}
```

## Troubleshooting Common Issues

### 1. Origin Mismatch

**Problem**: Frontend on `127.0.0.1:3000` but API expects `localhost:3000`

**Solution**: Use consistent hostnames in both frontend and backend configuration

### 2. Missing CORS Headers

**Problem**: Backend not sending proper CORS headers

**Solution**: Verify backend CORS configuration includes frontend origin

### 3. Preflight Request Failures

**Problem**: OPTIONS requests failing

**Solution**: Ensure backend handles preflight requests for all endpoints

## Environment Configuration

Ensure your `.env.development` file uses consistent URLs:

```bash
# Good - consistent hostname
NEXT_PUBLIC_API_URL=http://localhost:8000

# Avoid - trailing slashes (handled automatically)
NEXT_PUBLIC_API_URL=http://localhost:8000/
```

## Console Output

The enhanced error handling provides structured console output:

```
🚨 CORS Error Detected
├── Error Details: { message, code, name }
├── Request Details: { url, method, headers }
├── Environment Info: { origins, baseURL }
└── Troubleshooting Steps: [...]
```

This makes it easy to identify and resolve CORS configuration issues during development.
