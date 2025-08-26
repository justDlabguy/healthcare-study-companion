"use client";

import React, { useState, useCallback } from 'react';
import { Search, X, Filter } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';

interface SearchFilters {
  minScore: number;
  documentIds: number[];
}

interface SearchInputProps {
  onSearch: (query: string, filters: SearchFilters) => void;
  onClear: () => void;
  isLoading?: boolean;
  placeholder?: string;
  availableDocuments?: Array<{ id: number; filename: string }>;
  className?: string;
}

export function SearchInput({
  onSearch,
  onClear,
  isLoading = false,
  placeholder = "Search through your documents...",
  availableDocuments = [],
  className = ""
}: SearchInputProps) {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    minScore: 0.1,
    documentIds: []
  });
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      onSearch(query.trim(), filters);
    }
  }, [query, filters, onSearch]);

  const handleClear = useCallback(() => {
    setQuery('');
    setFilters({
      minScore: 0.1,
      documentIds: []
    });
    onClear();
  }, [onClear]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const toggleDocumentFilter = (documentId: number) => {
    setFilters(prev => ({
      ...prev,
      documentIds: prev.documentIds.includes(documentId)
        ? prev.documentIds.filter(id => id !== documentId)
        : [...prev.documentIds, documentId]
    }));
  };

  const clearDocumentFilters = () => {
    setFilters(prev => ({ ...prev, documentIds: [] }));
  };

  const hasActiveFilters = filters.minScore > 0.1 || filters.documentIds.length > 0;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder={placeholder}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            className="pl-10 pr-10"
            disabled={isLoading}
          />
          {query && (
            <button
              onClick={handleClear}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              disabled={isLoading}
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        
        <Button
          onClick={handleSearch}
          disabled={!query.trim() || isLoading}
          className="px-6"
        >
          {isLoading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            'Search'
          )}
        </Button>

        {availableDocuments.length > 0 && (
          <Popover open={showFilters} onOpenChange={setShowFilters}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                className={hasActiveFilters ? "border-blue-500 bg-blue-50" : ""}
              >
                <Filter className="h-4 w-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80" align="end">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Minimum Relevance Score</Label>
                  <div className="px-2">
                    <Slider
                      value={[filters.minScore]}
                      onValueChange={(value) => setFilters(prev => ({ ...prev, minScore: value[0] }))}
                      max={1}
                      min={0}
                      step={0.1}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>0.0</span>
                      <span className="font-medium">{filters.minScore.toFixed(1)}</span>
                      <span>1.0</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-sm font-medium">Filter by Documents</Label>
                    {filters.documentIds.length > 0 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={clearDocumentFilters}
                        className="h-auto p-1 text-xs"
                      >
                        Clear all
                      </Button>
                    )}
                  </div>
                  <div className="max-h-40 overflow-y-auto space-y-2">
                    {availableDocuments.map((doc) => (
                      <div key={doc.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`doc-${doc.id}`}
                          checked={filters.documentIds.includes(doc.id)}
                          onCheckedChange={() => toggleDocumentFilter(doc.id)}
                        />
                        <Label
                          htmlFor={`doc-${doc.id}`}
                          className="text-sm truncate flex-1 cursor-pointer"
                          title={doc.filename}
                        >
                          {doc.filename}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        )}
      </div>

      {/* Active filters display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2">
          {filters.minScore > 0.1 && (
            <Badge variant="secondary" className="text-xs">
              Min Score: {filters.minScore.toFixed(1)}
              <button
                onClick={() => setFilters(prev => ({ ...prev, minScore: 0.1 }))}
                className="ml-1 hover:text-red-600"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.documentIds.map((docId) => {
            const doc = availableDocuments.find(d => d.id === docId);
            return doc ? (
              <Badge key={docId} variant="secondary" className="text-xs">
                {doc.filename}
                <button
                  onClick={() => toggleDocumentFilter(docId)}
                  className="ml-1 hover:text-red-600"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ) : null;
          })}
        </div>
      )}
    </div>
  );
}