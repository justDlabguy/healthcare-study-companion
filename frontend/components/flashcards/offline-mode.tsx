"use client";

import React from "react";
import { WifiOff, BookOpen, Download, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface OfflineModeProps {
  onRetry?: () => void;
  onUseCache?: () => void;
  cachedItemsCount?: number;
  isRetrying?: boolean;
}

export function OfflineMode({
  onRetry,
  onUseCache,
  cachedItemsCount = 0,
  isRetrying = false,
}: OfflineModeProps) {
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <WifiOff className="h-5 w-5 text-gray-500" />
          Offline Mode
        </CardTitle>
        <CardDescription>
          You're currently offline, but we can still help you study!
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert>
          <BookOpen className="h-4 w-4" />
          <AlertTitle>Study Offline</AlertTitle>
          <AlertDescription>
            While you're offline, you can still review previously generated
            flashcards and study materials that are cached on your device.
          </AlertDescription>
        </Alert>

        {cachedItemsCount > 0 && (
          <Alert className="border-blue-200 bg-blue-50">
            <Download className="h-4 w-4" />
            <AlertTitle className="text-blue-800">
              Cached Content Available
            </AlertTitle>
            <AlertDescription className="text-blue-700">
              You have {cachedItemsCount} cached flashcard sets available for
              offline study.
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <h4 className="font-medium">What you can do offline:</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
            <li>Review previously generated flashcards</li>
            <li>Study cached content from your topics</li>
            <li>Continue your spaced repetition schedule</li>
            <li>View your study progress and statistics</li>
          </ul>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium">When you're back online:</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
            <li>Generate new flashcards with AI</li>
            <li>Upload and process new documents</li>
            <li>Sync your progress across devices</li>
            <li>Access the latest features and updates</li>
          </ul>
        </div>

        <div className="flex gap-2 flex-wrap">
          {cachedItemsCount > 0 && onUseCache && (
            <Button onClick={onUseCache} className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Study Cached Content
            </Button>
          )}

          {onRetry && (
            <Button
              variant="outline"
              onClick={onRetry}
              disabled={isRetrying}
              className="flex items-center gap-2"
            >
              {isRetrying ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Checking Connection...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Try to Reconnect
                </>
              )}
            </Button>
          )}
        </div>

        <div className="text-xs text-gray-500 mt-4">
          Your study progress will be synced automatically when you reconnect.
        </div>
      </CardContent>
    </Card>
  );
}

export default OfflineMode;
