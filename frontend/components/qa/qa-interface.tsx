'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { useConfirmDialog } from '@/hooks/use-confirm-dialog';
import { useErrorToast } from '@/hooks/use-error-toast';
import { useApiRetry } from '@/hooks/use-retry';
import { 
  MessageCircle, 
  Send, 
  Copy, 
  Trash2, 
  Bot, 
  User,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { LoadingState } from '@/components/ui/loading-state';
import { StatusMessage } from '@/components/ui/status-message';
import { QAResponse } from '@/lib/api';

interface QAInterfaceProps {
  topicId: number;
  topicTitle: string;
  hasDocuments: boolean;
}

export function QAInterface({ topicId, topicTitle, hasDocuments }: QAInterfaceProps) {
  const [messages, setMessages] = useState<QAResponse[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isAsking, setIsAsking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const { showConfirmDialog } = useConfirmDialog();
  const { showError, showSuccess } = useErrorToast();

  // Load Q&A history on component mount
  useEffect(() => {
    loadQAHistory();
  }, [topicId]);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadQAHistory = async () => {
    try {
      setIsLoading(true);
      const { qaApi } = await import('@/lib/api');
      const historyResponse = await qaApi.getQAHistory(topicId);
      setMessages(historyResponse.items || []);
    } catch (error) {
      console.error('Failed to load Q&A history:', error);
      
      // Only show error if it's not a 404 (empty history)
      if (error instanceof Error && !error.message.includes('404')) {
        showError(error, {
          title: 'Failed to Load History',
          onRetry: loadQAHistory
        });
      }
      
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentQuestion.trim()) return;

    if (!hasDocuments) {
      toast({
        title: 'No Documents',
        description: 'Please upload documents first to ask questions.',
        variant: 'destructive'
      });
      return;
    }

    const question = currentQuestion.trim();
    setCurrentQuestion('');
    setIsAsking(true);

    try {
      const { qaApi } = await import('@/lib/api');
      const response = await qaApi.askQuestion(topicId, question);
      setMessages(prev => [...prev, response]);
    } catch (error) {
      console.error('Failed to ask question:', error);
      
      showError(error, {
        title: 'Question Failed',
        onRetry: () => {
          setCurrentQuestion(question);
          handleAskQuestion({ preventDefault: () => {} } as any);
        }
      });
      
      // Add error message to chat
      const errorResponse: QAResponse = {
        id: Date.now(),
        question,
        answer: 'Sorry, I encountered an error while processing your question. Please try again or check your connection.',
        topic_id: topicId,
        created_at: new Date().toISOString(),
        confidence: 0
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsAsking(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAskQuestion(e as any);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: 'Copied',
        description: 'Answer copied to clipboard'
      });
    } catch (error) {
      toast({
        title: 'Copy Failed',
        description: 'Failed to copy text to clipboard',
        variant: 'destructive'
      });
    }
  };

  const deleteMessage = async (messageId: number) => {
    const confirmed = await showConfirmDialog({
      title: 'Delete Q&A',
      message: 'Are you sure you want to delete this question and answer?'
    });

    if (!confirmed) return;

    try {
      const { qaApi } = await import('@/lib/api');
      await qaApi.deleteQA(topicId, messageId);
      setMessages(prev => prev.filter(msg => msg.id !== messageId));
      
      toast({
        title: 'Deleted',
        description: 'Q&A entry deleted successfully'
      });
    } catch (error) {
      console.error('Failed to delete Q&A:', error);
      toast({
        title: 'Delete Failed',
        description: 'Failed to delete Q&A entry',
        variant: 'destructive'
      });
    }
  };

  const clearAllHistory = async () => {
    const confirmed = await showConfirmDialog({
      title: 'Clear All History',
      message: 'Are you sure you want to delete all Q&A history for this topic? This action cannot be undone.'
    });

    if (!confirmed) return;

    try {
      const { qaApi } = await import('@/lib/api');
      await qaApi.deleteAllQA(topicId);
      setMessages([]);
      
      toast({
        title: 'History Cleared',
        description: 'All Q&A history has been deleted'
      });
    } catch (error) {
      console.error('Failed to clear history:', error);
      toast({
        title: 'Clear Failed',
        description: 'Failed to clear Q&A history',
        variant: 'destructive'
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <LoadingState 
            message="Loading Q&A history..." 
            size="lg"
            variant="primary"
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col h-[600px] sm:h-[700px]">
      <CardHeader className="flex-shrink-0">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <CardTitle className="flex items-center gap-2 min-w-0">
            <MessageCircle className="h-5 w-5 flex-shrink-0" />
            <span className="truncate">Q&A: {topicTitle}</span>
          </CardTitle>
          {messages.length > 0 && (
            <Button
              onClick={clearAllHistory}
              variant="outline"
              size="sm"
              className="text-red-600 hover:text-red-700 w-full sm:w-auto"
            >
              Clear History
            </Button>
          )}
        </div>
        {!hasDocuments && (
          <StatusMessage
            status="warning"
            message="Upload documents first to start asking questions"
          />
        )}
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-6">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Start a Conversation</h3>
              <p className="text-gray-600">
                {hasDocuments 
                  ? 'Ask questions about your uploaded documents and get AI-powered answers.'
                  : 'Upload documents first, then ask questions about their content.'
                }
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="space-y-4">
                {/* Question */}
                <div className="flex justify-end">
                  <div className="max-w-[85%] sm:max-w-3xl bg-blue-600 text-white rounded-lg px-3 sm:px-4 py-3">
                    <div className="flex items-start gap-2">
                      <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium mb-1">You asked:</p>
                        <p className="break-words">{message.question}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Answer */}
                <div className="flex justify-start">
                  <div className="max-w-[85%] sm:max-w-3xl bg-gray-100 rounded-lg px-3 sm:px-4 py-3">
                    <div className="flex items-start gap-2">
                      <Bot className="h-4 w-4 mt-0.5 flex-shrink-0 text-blue-600" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-medium text-gray-900">AI Assistant</p>
                          <div className="flex items-center gap-1 flex-shrink-0">
                            <Button
                              onClick={() => copyToClipboard(message.answer)}
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0 text-gray-500 hover:text-gray-700"
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                            <Button
                              onClick={() => deleteMessage(message.id)}
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0 text-gray-500 hover:text-red-600"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        <p className="text-gray-800 whitespace-pre-wrap mb-2 break-words">{message.answer}</p>
                        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 text-xs text-gray-500">
                          <span>{new Date(message.created_at).toLocaleString()}</span>
                          {message.confidence && (
                            <span>Confidence: {Math.round(message.confidence * 100)}%</span>
                          )}
                          {message.model && (
                            <span>Model: {message.model}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}

          {/* Loading indicator */}
          {isAsking && (
            <div className="flex justify-start">
              <div className="max-w-[85%] sm:max-w-3xl bg-gray-100 rounded-lg px-3 sm:px-4 py-3">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4 text-blue-600" />
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                  <p className="text-gray-600">AI is analyzing your documents and generating an answer...</p>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Question Input */}
        <form onSubmit={handleAskQuestion} className="flex gap-2">
          <Input
            value={currentQuestion}
            onChange={(e) => setCurrentQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={hasDocuments ? "Ask a question about your documents..." : "Upload documents first to ask questions"}
            disabled={isAsking || !hasDocuments}
            className="flex-1 min-w-0"
          />
          <Button 
            type="submit" 
            disabled={!currentQuestion.trim() || isAsking || !hasDocuments}
            className="px-3 flex-shrink-0"
          >
            {isAsking ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>

        <p className="text-xs text-gray-500 mt-2 hidden sm:block">
          Press Enter to send, Shift+Enter for new line
        </p>
      </CardContent>
    </Card>
  );
}