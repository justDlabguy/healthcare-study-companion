"use client";

import React, { useState, useEffect } from "react";
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Activity,
  Zap,
  Shield,
  Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { api } from "@/lib/api";

interface ProviderHealth {
  status: string;
  last_check: string | null;
  response_time_ms: number | null;
  error_count: number;
  success_count: number;
  consecutive_failures: number;
  failure_rate: number;
  circuit_breaker_state: string;
  is_degraded: boolean;
  degradation_reason: string | null;
}

interface SystemHealth {
  system_status: string;
  available_providers: string[];
  total_providers: number;
  provider_health: Record<string, ProviderHealth>;
  circuit_breaker_metrics: Record<string, any>;
  degradation_stats: {
    mock_generations: number;
    cache_hits: number;
    template_generations: number;
    total_fallbacks: number;
    cache_size: number;
    cache_hit_rate: number;
  };
  fallback_available: boolean;
  last_updated: string;
}

interface SystemStatusProps {
  topicId?: number;
  compact?: boolean;
  showDetails?: boolean;
}

export function SystemStatus({
  topicId,
  compact = false,
  showDetails = false,
}: SystemStatusProps) {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchHealth = async () => {
    try {
      setError(null);
      const endpoint = topicId
        ? `/topics/${topicId}/flashcards/system/health`
        : "/topics/1/flashcards/system/health"; // Fallback endpoint

      const response = await api.get(endpoint);
      setHealth(response.data);
    } catch (err: any) {
      console.error("Failed to fetch system health:", err);
      setError(err.response?.data?.detail || "Failed to fetch system status");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchHealth();
  };

  const handleProviderRecovery = async (provider: string) => {
    try {
      const endpoint = topicId
        ? `/topics/${topicId}/flashcards/system/recovery/${provider}`
        : `/topics/1/flashcards/system/recovery/${provider}`;

      await api.post(endpoint);
      await fetchHealth(); // Refresh after recovery attempt
    } catch (err: any) {
      console.error(`Failed to recover provider ${provider}:`, err);
    }
  };

  useEffect(() => {
    fetchHealth();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [topicId]);

  if (loading) {
    return (
      <Card className={compact ? "p-4" : ""}>
        <CardContent className={compact ? "p-0" : ""}>
          <div className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 animate-spin" />
            <span className="text-sm">Checking system status...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={compact ? "p-4" : ""}>
        <CardContent className={compact ? "p-0" : ""}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-600">Status unavailable</span>
            </div>
            <Button variant="outline" size="sm" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!health) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "degraded":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-100 text-green-800";
      case "degraded":
        return "bg-yellow-100 text-yellow-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (compact) {
    return (
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(health.system_status)}
            <span className="text-sm font-medium">
              AI Service: {health.available_providers.length}/
              {health.total_providers} providers
            </span>
            {health.degradation_stats.total_fallbacks > 0 && (
              <Badge variant="outline" className="text-xs">
                <Shield className="h-3 w-3 mr-1" />
                Backup active
              </Badge>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw
              className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`}
            />
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(health.system_status)}
              Flashcard Generation System
            </CardTitle>
            <CardDescription>
              AI service status and backup system information
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Status */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-3">
            {getStatusIcon(health.system_status)}
            <div>
              <div className="font-medium">System Status</div>
              <div className="text-sm text-gray-600">
                {health.available_providers.length} of {health.total_providers}{" "}
                AI providers available
              </div>
            </div>
          </div>
          <Badge className={getStatusColor(health.system_status)}>
            {health.system_status}
          </Badge>
        </div>

        {/* Provider Health */}
        {showDetails && (
          <div className="space-y-3">
            <h4 className="font-medium flex items-center gap-2">
              <Zap className="h-4 w-4" />
              AI Provider Status
            </h4>
            <div className="grid gap-3">
              {Object.entries(health.provider_health).map(
                ([provider, providerHealth]) => (
                  <div
                    key={provider}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      {getStatusIcon(providerHealth.status)}
                      <div>
                        <div className="font-medium capitalize">{provider}</div>
                        <div className="text-sm text-gray-600">
                          {providerHealth.response_time_ms
                            ? `${providerHealth.response_time_ms.toFixed(
                                0
                              )}ms response time`
                            : "No recent activity"}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant="outline"
                        className={getStatusColor(providerHealth.status)}
                      >
                        {providerHealth.circuit_breaker_state}
                      </Badge>
                      {providerHealth.status === "failed" && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleProviderRecovery(provider)}
                        >
                          Retry
                        </Button>
                      )}
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {/* Backup System Stats */}
        {health.degradation_stats.total_fallbacks > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Backup System Activity
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {health.degradation_stats.total_fallbacks}
                </div>
                <div className="text-sm text-blue-600">Total Fallbacks</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {health.degradation_stats.cache_hits}
                </div>
                <div className="text-sm text-green-600">Cache Hits</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {health.degradation_stats.mock_generations}
                </div>
                <div className="text-sm text-purple-600">Mock Generated</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {health.degradation_stats.cache_hit_rate.toFixed(1)}%
                </div>
                <div className="text-sm text-orange-600">Cache Hit Rate</div>
              </div>
            </div>
          </div>
        )}

        {/* Last Updated */}
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          Last updated: {new Date(health.last_updated).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );
}

export default SystemStatus;
