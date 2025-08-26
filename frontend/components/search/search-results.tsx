"use client";

import React from 'react';
import { FileText, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingState } from '@/components/ui/loading-state';
import { SearchResult } from '@/lib/api';

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  isLoading?: boolean;
  executionTime?: number;
  onResultClick?: (result: SearchResult) => void;
  className?: string;
}

export function SearchResults({
  results,
  query,
  isLoading = false,
  executionTime,
  onResultClick,
  className = ""
}: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className={className}>
        <LoadingState 
          message="Searching through your documents using AI-powered semantic search..."
          size="lg"
          variant="primary"
        />
      </div>
    );
  }

  if (results.length === 0 && query) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
        <p className="text-gray-500 max-w-md mx-auto">
          We couldn't find any content matching "{query}". Try adjusting your search terms or filters.
        </p>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 0.8) return '🎯';
    if (score >= 0.6) return '👍';
    return '📄';
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Results header */}
      {results.length > 0 && (
        <div className="flex items-center justify-between text-sm text-gray-600 pb-2 border-b">
          <span>
            Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
          </span>
          {executionTime && (
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              <span>{executionTime.toFixed(0)}ms</span>
            </div>
          )}
        </div>
      )}

      {/* Results list */}
      <div className="space-y-3">
        {results.map((result, index) => (
          <Card 
            key={`${result.chunk_id}-${index}`} 
            className={`transition-all hover:shadow-md ${onResultClick ? 'cursor-pointer' : ''}`}
            onClick={() => onResultClick?.(result)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <FileText className="h-4 w-4 text-gray-500 flex-shrink-0" />
                  <span className="font-medium text-sm truncate" title={result.document_filename}>
                    {result.document_filename}
                  </span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Badge 
                    variant="secondary" 
                    className={`text-xs ${getScoreColor(result.score)}`}
                  >
                    <span className="mr-1">{getScoreIcon(result.score)}</span>
                    {(result.score * 100).toFixed(0)}%
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                <p className="text-sm text-gray-700 leading-relaxed">
                  {result.snippet}
                </p>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Chunk {result.chunk_index + 1}</span>
                  {result.chunk_metadata && Object.keys(result.chunk_metadata).length > 0 && (
                    <div className="flex gap-1">
                      {Object.entries(result.chunk_metadata).map(([key, value]) => (
                        <Badge key={key} variant="outline" className="text-xs">
                          {key}: {String(value)}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Load more button placeholder */}
      {results.length >= 10 && (
        <div className="text-center pt-4">
          <Button variant="outline" disabled>
            Load More Results
          </Button>
          <p className="text-xs text-gray-500 mt-2">
            Pagination coming soon
          </p>
        </div>
      )}
    </div>
  );
}