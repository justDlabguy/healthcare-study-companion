'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { 
  Brain, 
  RotateCcw, 
  ChevronLeft, 
  ChevronRight, 
  Eye,
  Loader2,
  AlertCircle,
  Trophy
} from 'lucide-react';
import { LoadingState } from '@/components/ui/loading-state';
import { StatusMessage } from '@/components/ui/status-message';
import { Flashcard } from '@/lib/api';

interface FlashcardInterfaceProps {
  topicId: number;
  topicTitle: string;
  hasDocuments: boolean;
}

interface SessionStats {
  correct: number;
  total: number;
  currentStreak: number;
  bestStreak: number;
}

export function FlashcardInterface({ topicId, topicTitle, hasDocuments }: FlashcardInterfaceProps) {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [sessionStats, setSessionStats] = useState<SessionStats>({
    correct: 0,
    total: 0,
    currentStreak: 0,
    bestStreak: 0
  });
  const [isReviewing, setIsReviewing] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadFlashcards();
  }, [topicId]);

  const loadFlashcards = async () => {
    try {
      setIsLoading(true);
      const { flashcardsApi } = await import('@/lib/api');
      
      // Try to get flashcards for review first, then all flashcards
      let cards = await flashcardsApi.getFlashcardsForReview(topicId, 20);
      if (cards.length === 0) {
        cards = await flashcardsApi.getFlashcards(topicId);
      }
      
      setFlashcards(cards);
      setCurrentCardIndex(0);
      setShowAnswer(false);
    } catch (error) {
      console.error('Failed to load flashcards:', error);
      setFlashcards([]);
    } finally {
      setIsLoading(false);
    }
  };

  const currentCard = flashcards[currentCardIndex];

  const handleNextCard = () => {
    if (currentCardIndex < flashcards.length - 1) {
      setCurrentCardIndex(prev => prev + 1);
      setShowAnswer(false);
    }
  };

  const handlePreviousCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(prev => prev - 1);
      setShowAnswer(false);
    }
  };

  const handleDifficultyRating = async (quality: number) => {
    if (!currentCard) return;

    setIsReviewing(true);
    
    try {
      const { flashcardsApi } = await import('@/lib/api');
      await flashcardsApi.reviewFlashcard(topicId, currentCard.id, quality);
      
      // Update session stats
      const isCorrect = quality >= 3; // Quality 3+ is considered correct
      setSessionStats(prev => ({
        correct: isCorrect ? prev.correct + 1 : prev.correct,
        total: prev.total + 1,
        currentStreak: isCorrect ? prev.currentStreak + 1 : 0,
        bestStreak: isCorrect 
          ? Math.max(prev.bestStreak, prev.currentStreak + 1)
          : prev.bestStreak
      }));

      const qualityLabels = ['Again', 'Hard', 'Good', 'Easy'];
      toast({
        title: 'Review Recorded',
        description: `Marked as "${qualityLabels[quality] || 'Unknown'}"`,
      });

      // Auto-advance to next card after a short delay
      setTimeout(() => {
        handleNextCard();
      }, 500);
    } catch (error) {
      console.error('Failed to review flashcard:', error);
      toast({
        title: 'Review Failed',
        description: 'Failed to record your review. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsReviewing(false);
    }
  };

  const resetSession = () => {
    setCurrentCardIndex(0);
    setShowAnswer(false);
    setSessionStats({
      correct: 0,
      total: 0,
      currentStreak: 0,
      bestStreak: 0
    });
    loadFlashcards(); // Reload flashcards
  };

  const generateFlashcards = async () => {
    try {
      setIsLoading(true);
      
      // For now, we'll show a message that this feature is coming soon
      toast({
        title: 'Feature Coming Soon',
        description: 'Automatic flashcard generation will be available soon. For now, you can create flashcards manually.',
      });
      
      // TODO: Implement actual flashcard generation
      // const { flashcardsApi } = await import('@/lib/api');
      // const generatedCards = await flashcardsApi.generateFlashcards(topicId, 'document content', 5);
      // setFlashcards(generatedCards);
    } catch (error) {
      console.error('Failed to generate flashcards:', error);
      toast({
        title: 'Generation Failed',
        description: 'Failed to generate flashcards. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <LoadingState 
            message="Loading flashcards..." 
            size="lg"
            variant="primary"
          />
        </CardContent>
      </Card>
    );
  }

  if (!hasDocuments) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Flashcards: {topicTitle}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center py-8">
            <StatusMessage
              status="warning"
              title="No Documents Available"
              message="Upload documents first to generate flashcards from your content."
            />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (flashcards.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Flashcards: {topicTitle}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center py-8">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Flashcards Available</h3>
            <p className="text-gray-600 mb-4">
              Generate flashcards from your uploaded documents to start studying.
            </p>
            <Button onClick={generateFlashcards} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                'Generate Flashcards'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const progressPercentage = ((currentCardIndex + 1) / flashcards.length) * 100;
  const accuracyPercentage = sessionStats.total > 0 
    ? Math.round((sessionStats.correct / sessionStats.total) * 100) 
    : 0;

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <CardTitle className="flex items-center gap-2 min-w-0">
              <Brain className="h-5 w-5 flex-shrink-0" />
              <span className="truncate">Flashcards: {topicTitle}</span>
            </CardTitle>
            <div className="flex gap-2">
              <Button onClick={resetSession} variant="outline" size="sm" className="w-full sm:w-auto">
                <RotateCcw className="h-4 w-4 mr-1" />
                Reset Session
              </Button>
            </div>
          </div>
          
          {/* Progress and Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{currentCardIndex + 1}</div>
              <div className="text-sm text-gray-600">of {flashcards.length}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{accuracyPercentage}%</div>
              <div className="text-sm text-gray-600">Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{sessionStats.currentStreak}</div>
              <div className="text-sm text-gray-600">Current Streak</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{sessionStats.bestStreak}</div>
              <div className="text-sm text-gray-600">Best Streak</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Progress</span>
              <span className="text-sm text-gray-600">{Math.round(progressPercentage)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Flashcard */}
      <Card className="min-h-[400px] sm:min-h-[500px]">
        <CardContent className="p-4 sm:p-8">
          <div className="text-center h-full flex flex-col justify-center">
            {/* Difficulty Badge */}
            {currentCard.difficulty && (
              <div className="mb-4">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                  currentCard.difficulty <= 0.3
                    ? 'bg-green-100 text-green-800'
                    : currentCard.difficulty <= 0.7
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {currentCard.difficulty <= 0.3 ? 'EASY' : 
                   currentCard.difficulty <= 0.7 ? 'MEDIUM' : 'HARD'}
                </span>
              </div>
            )}

            {/* Question */}
            <div className="mb-6 sm:mb-8">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4">Question:</h2>
              <p className="text-base sm:text-lg text-gray-700 break-words">{currentCard.front}</p>
            </div>

            {/* Answer */}
            {showAnswer ? (
              <div className="mb-6 sm:mb-8">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">Answer:</h3>
                <div className="bg-blue-50 p-4 sm:p-6 rounded-lg">
                  <p className="text-gray-800 whitespace-pre-wrap break-words">{currentCard.back}</p>
                </div>
              </div>
            ) : (
              <div className="mb-6 sm:mb-8">
                <Button onClick={() => setShowAnswer(true)} size="lg" className="w-full sm:w-auto">
                  <Eye className="h-4 w-4 mr-2" />
                  Show Answer
                </Button>
              </div>
            )}

            {/* Difficulty Rating (shown after answer is revealed) */}
            {showAnswer && (
              <div className="mb-6">
                <p className="text-sm text-gray-600 mb-4">How well did you know this?</p>
                <div className="grid grid-cols-2 sm:flex gap-2 justify-center">
                  <Button 
                    onClick={() => handleDifficultyRating(0)}
                    disabled={isReviewing}
                    variant="outline"
                    className="text-red-600 border-red-200 hover:bg-red-50"
                    size="sm"
                  >
                    Again
                  </Button>
                  <Button 
                    onClick={() => handleDifficultyRating(1)}
                    disabled={isReviewing}
                    variant="outline"
                    className="text-orange-600 border-orange-200 hover:bg-orange-50"
                    size="sm"
                  >
                    Hard
                  </Button>
                  <Button 
                    onClick={() => handleDifficultyRating(3)}
                    disabled={isReviewing}
                    variant="outline"
                    className="text-blue-600 border-blue-200 hover:bg-blue-50"
                    size="sm"
                  >
                    Good
                  </Button>
                  <Button 
                    onClick={() => handleDifficultyRating(5)}
                    disabled={isReviewing}
                    variant="outline"
                    className="text-green-600 border-green-200 hover:bg-green-50"
                    size="sm"
                  >
                    Easy
                  </Button>
                </div>
                {isReviewing && (
                  <div className="mt-3">
                    <StatusMessage
                      status="loading"
                      message="Recording your review and updating spaced repetition schedule..."
                      showIcon={false}
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <Button 
          onClick={handlePreviousCard}
          disabled={currentCardIndex === 0}
          variant="outline"
          className="w-full sm:w-auto"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Previous
        </Button>

        <div className="text-sm text-gray-500 text-center">
          {sessionStats.total > 0 && (
            <span>
              Session: {sessionStats.correct}/{sessionStats.total} correct
            </span>
          )}
        </div>

        <Button 
          onClick={handleNextCard}
          disabled={currentCardIndex === flashcards.length - 1}
          variant="outline"
          className="w-full sm:w-auto"
        >
          Next
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>

      {/* Session Complete */}
      {currentCardIndex === flashcards.length - 1 && showAnswer && (
        <Card>
          <CardContent className="p-6 text-center">
            <Trophy className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Session Complete!</h3>
            <p className="text-gray-600 mb-4">
              You've reviewed all {flashcards.length} flashcards.
            </p>
            <div className="grid grid-cols-2 gap-4 mb-6 max-w-md mx-auto">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{sessionStats.correct}</div>
                <div className="text-sm text-gray-600">Correct</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{accuracyPercentage}%</div>
                <div className="text-sm text-gray-600">Accuracy</div>
              </div>
            </div>
            <div className="flex gap-2 justify-center">
              <Button onClick={resetSession}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Start Over
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}