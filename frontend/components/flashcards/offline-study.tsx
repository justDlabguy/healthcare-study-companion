"use client";

import React, { useState, useEffect } from "react";
import {
  BookOpen,
  Lightbulb,
  Heart,
  RefreshCw,
  Download,
  WifiOff,
  CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { useOfflineMode } from "@/hooks/use-offline-mode";
import { api } from "@/lib/api";

interface OfflineStudyProps {
  topicId: number;
  topicTitle: string;
  onReturnOnline?: () => void;
}

interface OfflineContent {
  session_id: string;
  created_at: string;
  content: {
    study_tips: string[];
    flashcards: Array<{ front: string; back: string }>;
    motivation: string[];
    study_guide: {
      title: string;
      sections: Array<{ title: string; content: string }>;
    };
    offline_message: string;
  };
  instructions: string[];
}

export function OfflineStudy({
  topicId,
  topicTitle,
  onReturnOnline,
}: OfflineStudyProps) {
  const [offlineContent, setOfflineContent] = useState<OfflineContent | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [currentFlashcard, setCurrentFlashcard] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [completedTips, setCompletedTips] = useState<Set<number>>(new Set());

  const {
    isOnline,
    cachedFlashcards,
    cachedTopics,
    totalCachedItems,
    getCachedFlashcards,
    getCacheStats,
  } = useOfflineMode();

  useEffect(() => {
    loadOfflineContent();
  }, [topicId]);

  const loadOfflineContent = async () => {
    try {
      setLoading(true);
      const response = await api.get(
        `/topics/${topicId}/flashcards/offline/content`
      );
      setOfflineContent(response.data);
    } catch (error) {
      console.error("Failed to load offline content:", error);
      // Create fallback content
      setOfflineContent({
        session_id: `offline_${Date.now()}`,
        created_at: new Date().toISOString(),
        content: {
          study_tips: [
            "Review your cached flashcards regularly",
            "Practice active recall techniques",
            "Organize your study materials",
          ],
          flashcards: [
            {
              front: "What should you do when studying offline?",
              back: "Review cached materials and practice active recall",
            },
          ],
          motivation: ["Keep learning, even offline!"],
          study_guide: {
            title: "Offline Study Guide",
            sections: [
              {
                title: "Review Cached Content",
                content:
                  "Use your previously downloaded materials to continue studying.",
              },
            ],
          },
          offline_message: `Continue studying ${topicTitle} with offline resources.`,
        },
        instructions: [
          "Review cached flashcards",
          "Practice active recall",
          "Organize study notes",
        ],
      });
    } finally {
      setLoading(false);
    }
  };

  const handleNextFlashcard = () => {
    if (
      offlineContent &&
      currentFlashcard < offlineContent.content.flashcards.length - 1
    ) {
      setCurrentFlashcard(currentFlashcard + 1);
      setShowAnswer(false);
    }
  };

  const handlePrevFlashcard = () => {
    if (currentFlashcard > 0) {
      setCurrentFlashcard(currentFlashcard - 1);
      setShowAnswer(false);
    }
  };

  const toggleTipCompletion = (index: number) => {
    const newCompleted = new Set(completedTips);
    if (newCompleted.has(index)) {
      newCompleted.delete(index);
    } else {
      newCompleted.add(index);
    }
    setCompletedTips(newCompleted);
  };

  const cacheStats = getCacheStats();
  const topicCachedFlashcards = getCachedFlashcards(topicId);

  if (loading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="flex items-center justify-center p-8">
          <RefreshCw className="h-6 w-6 animate-spin mr-2" />
          <span>Loading offline content...</span>
        </CardContent>
      </Card>
    );
  }

  if (!offlineContent) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-8 text-center">
          <WifiOff className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold mb-2">
            Offline Content Unavailable
          </h3>
          <p className="text-gray-600">
            Unable to load offline study materials.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Offline Status Header */}
      <Alert className="border-blue-200 bg-blue-50">
        <WifiOff className="h-4 w-4" />
        <AlertTitle className="text-blue-800">Offline Study Mode</AlertTitle>
        <AlertDescription className="text-blue-700">
          {offlineContent.content.offline_message}
        </AlertDescription>
      </Alert>

      {/* Cache Statistics */}
      {totalCachedItems > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Cached Content Available
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {topicCachedFlashcards.length}
                </div>
                <div className="text-sm text-gray-600">Topic Flashcards</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {cacheStats.totalFlashcards}
                </div>
                <div className="text-sm text-gray-600">Total Cached</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {cacheStats.totalTopics}
                </div>
                <div className="text-sm text-gray-600">Cached Topics</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {cacheStats.cacheSizeKB}KB
                </div>
                <div className="text-sm text-gray-600">Cache Size</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Offline Flashcards */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Offline Flashcards
            </CardTitle>
            <CardDescription>
              Practice with these offline study cards
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {offlineContent.content.flashcards.length > 0 && (
              <>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-2">
                    Card {currentFlashcard + 1} of{" "}
                    {offlineContent.content.flashcards.length}
                  </div>
                  <div className="text-lg font-medium mb-4">
                    {offlineContent.content.flashcards[currentFlashcard].front}
                  </div>
                  {showAnswer && (
                    <div className="border-t pt-4">
                      <div className="text-gray-700">
                        {
                          offlineContent.content.flashcards[currentFlashcard]
                            .back
                        }
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowAnswer(!showAnswer)}
                  >
                    {showAnswer ? "Hide Answer" : "Show Answer"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handlePrevFlashcard}
                    disabled={currentFlashcard === 0}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleNextFlashcard}
                    disabled={
                      currentFlashcard ===
                      offlineContent.content.flashcards.length - 1
                    }
                  >
                    Next
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Study Tips */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Study Tips
            </CardTitle>
            <CardDescription>Offline study strategies and tips</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {offlineContent.content.study_tips.map((tip, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleTipCompletion(index)}
                    className="p-1 h-6 w-6"
                  >
                    <CheckCircle
                      className={`h-4 w-4 ${
                        completedTips.has(index)
                          ? "text-green-600"
                          : "text-gray-400"
                      }`}
                    />
                  </Button>
                  <div
                    className={`text-sm ${
                      completedTips.has(index)
                        ? "line-through text-gray-500"
                        : "text-gray-700"
                    }`}
                  >
                    {tip}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Study Guide */}
      <Card>
        <CardHeader>
          <CardTitle>{offlineContent.content.study_guide.title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {offlineContent.content.study_guide.sections.map(
              (section, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium mb-2">{section.title}</h4>
                  <p className="text-sm text-gray-600">{section.content}</p>
                </div>
              )
            )}
          </div>
        </CardContent>
      </Card>

      {/* Motivation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" />
            Stay Motivated
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
            <p className="text-lg font-medium text-gray-800">
              {offlineContent.content.motivation[0]}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Return Online Button */}
      {isOnline && onReturnOnline && (
        <div className="text-center">
          <Button onClick={onReturnOnline} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Return to Online Mode
          </Button>
        </div>
      )}
    </div>
  );
}

export default OfflineStudy;
