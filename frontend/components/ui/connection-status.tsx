'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Wifi, 
  WifiOff, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw,
  Settings,
  ExternalLink
} from 'lucide-react';
import { testCorsConfiguration, checkCorsConfiguration, getCorsTroubleshootingSteps } from '@/lib/cors-utils';

interface ConnectionStatusProps {
  apiUrl?: string;
  showDetails?: boolean;
  onRetry?: () => void;
}

export function ConnectionStatus({ 
  apiUrl, 
  showDetails = false, 
  onRetry 
}: ConnectionStatusProps) {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected' | 'cors-error'>('checking');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [errorDetails, setErrorDetails] = useState<string>('');
  const [corsIssues, setCorsIssues] = useState<{
    hasIssues: boolean;
    issues: string[];
    suggestions: string[];
  }>({ hasIssues: false, issues: [], suggestions: [] });

  const checkConnection = async () => {
    setStatus('checking');
    
    try {
      const result = await testCorsConfiguration(apiUrl);
      
      if (result.success) {
        setStatus('connected');
        setErrorDetails('');
      } else {
        if (result.corsInfo?.isCorsError) {
          setStatus('cors-error');
          setErrorDetails(result.corsInfo.suggestedFix || result.error || 'CORS error detected');
        } else {
          setStatus('disconnected');
          setErrorDetails(result.error || 'Connection failed');
        }
      }
    } catch (error) {
      setStatus('disconnected');
      setErrorDetails(error instanceof Error ? error.message : 'Unknown error');
    }
    
    setLastChecked(new Date());
  };

  useEffect(() => {
    checkConnection();
    
    // Check CORS configuration
    const corsCheck = checkCorsConfiguration();
    setCorsIssues(corsCheck);
    
    // Set up periodic checks
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, [apiUrl]);

  const handleRetry = () => {
    checkConnection();
    if (onRetry) {
      onRetry();
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'checking':
        return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'cors-error':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'disconnected':
        return <WifiOff className="h-4 w-4 text-red-500" />;
      default:
        return <Wifi className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'checking':
        return 'Checking connection...';
      case 'connected':
        return 'Connected';
      case 'cors-error':
        return 'CORS Configuration Issue';
      case 'disconnected':
        return 'Disconnected';
      default:
        return 'Unknown';
    }
  };

  const getStatusVariant = (): 'default' | 'secondary' | 'destructive' | 'outline' => {
    switch (status) {
      case 'connected':
        return 'default';
      case 'cors-error':
        return 'secondary';
      case 'disconnected':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  if (!showDetails) {
    return (
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <Badge variant={getStatusVariant()}>
          {getStatusText()}
        </Badge>
        {status !== 'connected' && (
          <Button
            onClick={handleRetry}
            size="sm"
            variant="outline"
            className="h-6 px-2"
          >
            <RefreshCw className="h-3 w-3" />
          </Button>
        )}
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {getStatusIcon()}
          Connection Status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <Badge variant={getStatusVariant()} className="mb-2">
              {getStatusText()}
            </Badge>
            {lastChecked && (
              <p className="text-sm text-gray-500">
                Last checked: {lastChecked.toLocaleTimeString()}
              </p>
            )}
          </div>
          <Button onClick={handleRetry} size="sm" variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>

        {/* API URL Info */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">API Configuration</h4>
          <div className="bg-gray-100 p-2 rounded text-sm font-mono break-all">
            {apiUrl || process.env.NEXT_PUBLIC_API_URL || 'Not configured'}
          </div>
        </div>

        {/* Error Details */}
        {errorDetails && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-red-600">Error Details</h4>
            <p className="text-sm text-red-700 bg-red-50 p-2 rounded">
              {errorDetails}
            </p>
          </div>
        )}

        {/* CORS Issues */}
        {corsIssues.hasIssues && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-yellow-600">Configuration Issues</h4>
            <div className="space-y-1">
              {corsIssues.issues.map((issue, index) => (
                <p key={index} className="text-sm text-yellow-700 bg-yellow-50 p-2 rounded">
                  {issue}
                </p>
              ))}
            </div>
            <div className="space-y-1">
              <h5 className="text-xs font-medium text-gray-600">Suggestions:</h5>
              {corsIssues.suggestions.map((suggestion, index) => (
                <p key={index} className="text-xs text-gray-600">
                  • {suggestion}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Troubleshooting Steps */}
        {status !== 'connected' && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Troubleshooting Steps</h4>
            <div className="space-y-1">
              {getCorsTroubleshootingSteps().slice(0, 4).map((step, index) => (
                <p key={index} className="text-xs text-gray-600">
                  {step}
                </p>
              ))}
            </div>
            <Button
              onClick={() => {
                const steps = getCorsTroubleshootingSteps();
                const fullSteps = steps.join('\n');
                navigator.clipboard.writeText(fullSteps).then(() => {
                  alert('Troubleshooting steps copied to clipboard');
                });
              }}
              size="sm"
              variant="outline"
              className="w-full"
            >
              Copy All Steps
            </Button>
          </div>
        )}

        {/* Quick Actions */}
        <div className="flex gap-2">
          <Button
            onClick={() => window.open(`${apiUrl || process.env.NEXT_PUBLIC_API_URL}/docs`, '_blank')}
            size="sm"
            variant="outline"
            className="flex-1"
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            API Docs
          </Button>
          <Button
            onClick={() => window.open('/api/health', '_blank')}
            size="sm"
            variant="outline"
            className="flex-1"
          >
            <Settings className="h-3 w-3 mr-1" />
            Health Check
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}