"use client";

import React, { useState, useCallback } from 'react';
import { SearchInput } from './search-input';
import { SearchResults } from './search-results';
import { searchApi, SearchResult, Document } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';

interface SearchFilters {
  minScore: number;
  documentIds: number[];
}

interface SearchInterfaceProps {
  topicId: number;
  documents?: Document[];
  onResultClick?: (result: SearchResult) => void;
  className?: string;
}

export function SearchInterface({
  topicId,
  documents = [],
  onResultClick,
  className = ""
}: SearchInterfaceProps) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [executionTime, setExecutionTime] = useState<number | undefined>();
  const { toast } = useToast();

  const handleSearch = useCallback(async (query: string, filters: SearchFilters) => {
    setIsLoading(true);
    setCurrentQuery(query);
    
    try {
      const searchQuery = {
        query,
        min_score: filters.minScore,
        document_ids: filters.documentIds.length > 0 ? filters.documentIds : undefined
      };

      const response = await searchApi.searchWithinTopic(topicId, searchQuery, 20);
      
      setResults(response.results);
      setExecutionTime(response.execution_time_ms);
      
      if (response.results.length === 0) {
        toast({
          title: "No results found",
          description: `No content found matching "${query}". Try different search terms or adjust filters.`,
          variant: "default"
        });
      } else {
        toast({
          title: "Search completed",
          description: `Found ${response.results.length} result${response.results.length !== 1 ? 's' : ''} in ${response.execution_time_ms?.toFixed(0) || 0}ms`,
          variant: "default"
        });
      }
    } catch (error) {
      console.error('Search failed:', error);
      toast({
        title: "Search failed",
        description: "An error occurred while searching. Please try again.",
        variant: "destructive"
      });
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [topicId, toast]);

  const handleClear = useCallback(() => {
    setResults([]);
    setCurrentQuery('');
    setExecutionTime(undefined);
  }, []);

  // Convert documents to the format expected by SearchInput
  const availableDocuments = documents
    .filter(doc => doc.status === 'PROCESSED')
    .map(doc => ({
      id: doc.id,
      filename: doc.filename
    }));

  return (
    <div className={`space-y-6 ${className}`}>
      <SearchInput
        onSearch={handleSearch}
        onClear={handleClear}
        isLoading={isLoading}
        availableDocuments={availableDocuments}
        placeholder="Search through your documents..."
      />
      
      <SearchResults
        results={results}
        query={currentQuery}
        isLoading={isLoading}
        executionTime={executionTime}
        onResultClick={onResultClick}
      />
    </div>
  );
}