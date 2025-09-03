"use client";

import { useState, useEffect, useCallback } from "react";

interface CachedFlashcard {
  id: string;
  front: string;
  back: string;
  topicId: number;
  cachedAt: string;
}

interface CachedTopic {
  id: number;
  title: string;
  flashcardCount: number;
  lastCached: string;
}

interface OfflineState {
  isOnline: boolean;
  cachedFlashcards: CachedFlashcard[];
  cachedTopics: CachedTopic[];
  totalCachedItems: number;
}

const CACHE_KEY_PREFIX = "healthcare_study_offline_";
const FLASHCARDS_CACHE_KEY = `${CACHE_KEY_PREFIX}flashcards`;
const TOPICS_CACHE_KEY = `${CACHE_KEY_PREFIX}topics`;

export function useOfflineMode() {
  const [state, setState] = useState<OfflineState>({
    isOnline: typeof navigator !== "undefined" ? navigator.onLine : true,
    cachedFlashcards: [],
    cachedTopics: [],
    totalCachedItems: 0,
  });

  // Load cached data from localStorage
  const loadCachedData = useCallback(() => {
    try {
      const cachedFlashcards = JSON.parse(
        localStorage.getItem(FLASHCARDS_CACHE_KEY) || "[]"
      );
      const cachedTopics = JSON.parse(
        localStorage.getItem(TOPICS_CACHE_KEY) || "[]"
      );

      setState((prev) => ({
        ...prev,
        cachedFlashcards,
        cachedTopics,
        totalCachedItems: cachedFlashcards.length + cachedTopics.length,
      }));
    } catch (error) {
      console.error("Error loading cached data:", error);
    }
  }, []);

  // Cache flashcards for offline use
  const cacheFlashcards = useCallback(
    (flashcards: any[], topicId: number) => {
      try {
        const cachedFlashcards = flashcards.map((card) => ({
          id: card.id.toString(),
          front: card.front,
          back: card.back,
          topicId,
          cachedAt: new Date().toISOString(),
        }));

        // Get existing cache
        const existingCache = JSON.parse(
          localStorage.getItem(FLASHCARDS_CACHE_KEY) || "[]"
        );

        // Remove old flashcards for this topic
        const filteredCache = existingCache.filter(
          (card: CachedFlashcard) => card.topicId !== topicId
        );

        // Add new flashcards
        const updatedCache = [...filteredCache, ...cachedFlashcards];

        // Limit cache size (keep only last 1000 flashcards)
        const limitedCache = updatedCache.slice(-1000);

        localStorage.setItem(
          FLASHCARDS_CACHE_KEY,
          JSON.stringify(limitedCache)
        );
        loadCachedData();
      } catch (error) {
        console.error("Error caching flashcards:", error);
      }
    },
    [loadCachedData]
  );

  // Cache topic information
  const cacheTopic = useCallback(
    (topic: any, flashcardCount: number) => {
      try {
        const cachedTopic = {
          id: topic.id,
          title: topic.title,
          flashcardCount,
          lastCached: new Date().toISOString(),
        };

        // Get existing cache
        const existingCache = JSON.parse(
          localStorage.getItem(TOPICS_CACHE_KEY) || "[]"
        );

        // Remove old entry for this topic
        const filteredCache = existingCache.filter(
          (t: CachedTopic) => t.id !== topic.id
        );

        // Add updated topic
        const updatedCache = [...filteredCache, cachedTopic];

        localStorage.setItem(TOPICS_CACHE_KEY, JSON.stringify(updatedCache));
        loadCachedData();
      } catch (error) {
        console.error("Error caching topic:", error);
      }
    },
    [loadCachedData]
  );

  // Get cached flashcards for a specific topic
  const getCachedFlashcards = useCallback(
    (topicId: number): CachedFlashcard[] => {
      return state.cachedFlashcards.filter((card) => card.topicId === topicId);
    },
    [state.cachedFlashcards]
  );

  // Clear cache for a specific topic
  const clearTopicCache = useCallback(
    (topicId: number) => {
      try {
        // Clear flashcards
        const flashcards = state.cachedFlashcards.filter(
          (card) => card.topicId !== topicId
        );
        localStorage.setItem(FLASHCARDS_CACHE_KEY, JSON.stringify(flashcards));

        // Clear topic
        const topics = state.cachedTopics.filter(
          (topic) => topic.id !== topicId
        );
        localStorage.setItem(TOPICS_CACHE_KEY, JSON.stringify(topics));

        loadCachedData();
      } catch (error) {
        console.error("Error clearing topic cache:", error);
      }
    },
    [state.cachedFlashcards, state.cachedTopics, loadCachedData]
  );

  // Clear all cache
  const clearAllCache = useCallback(() => {
    try {
      localStorage.removeItem(FLASHCARDS_CACHE_KEY);
      localStorage.removeItem(TOPICS_CACHE_KEY);
      loadCachedData();
    } catch (error) {
      console.error("Error clearing all cache:", error);
    }
  }, [loadCachedData]);

  // Check if we have cached content for a topic
  const hasCachedContent = useCallback(
    (topicId: number): boolean => {
      return state.cachedFlashcards.some((card) => card.topicId === topicId);
    },
    [state.cachedFlashcards]
  );

  // Get cache statistics
  const getCacheStats = useCallback(() => {
    const totalFlashcards = state.cachedFlashcards.length;
    const totalTopics = state.cachedTopics.length;
    const cacheSize =
      JSON.stringify(state.cachedFlashcards).length +
      JSON.stringify(state.cachedTopics).length;

    return {
      totalFlashcards,
      totalTopics,
      cacheSizeKB: Math.round(cacheSize / 1024),
      oldestCache:
        state.cachedFlashcards.length > 0
          ? Math.min(
              ...state.cachedFlashcards.map((card) =>
                new Date(card.cachedAt).getTime()
              )
            )
          : null,
      newestCache:
        state.cachedFlashcards.length > 0
          ? Math.max(
              ...state.cachedFlashcards.map((card) =>
                new Date(card.cachedAt).getTime()
              )
            )
          : null,
    };
  }, [state.cachedFlashcards, state.cachedTopics]);

  // Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      setState((prev) => ({ ...prev, isOnline: true }));
    };

    const handleOffline = () => {
      setState((prev) => ({ ...prev, isOnline: false }));
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // Load cached data on mount
    loadCachedData();

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [loadCachedData]);

  return {
    ...state,
    cacheFlashcards,
    cacheTopic,
    getCachedFlashcards,
    clearTopicCache,
    clearAllCache,
    hasCachedContent,
    getCacheStats,
  };
}

export type { CachedFlashcard, CachedTopic, OfflineState };
