'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { topicsApi, type Topic } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Home, 
  Plus, 
  Search, 
  BookOpen, 
  FileText, 
  MessageSquare, 
  Brain,
  X,
  ChevronRight,
  ChevronDown
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { isAuthenticated } = useAuth();
  const pathname = usePathname();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredTopics, setFilteredTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedTopics, setExpandedTopics] = useState<Set<number>>(new Set());

  // Load topics when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadTopics();
    }
  }, [isAuthenticated]);

  // Filter topics based on search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredTopics(topics);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = topics.filter(topic =>
        topic.title.toLowerCase().includes(query) ||
        (topic.description && topic.description.toLowerCase().includes(query))
      );
      setFilteredTopics(filtered);
    }
  }, [topics, searchQuery]);

  const loadTopics = async () => {
    try {
      setIsLoading(true);
      const data = await topicsApi.getTopics();
      setTopics(data);
    } catch (error) {
      console.error('Failed to load topics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTopicExpansion = (topicId: number) => {
    const newExpanded = new Set(expandedTopics);
    if (newExpanded.has(topicId)) {
      newExpanded.delete(topicId);
    } else {
      newExpanded.add(topicId);
    }
    setExpandedTopics(newExpanded);
  };

  const isActiveLink = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  const getTopicSubPages = (topicId: number) => [
    { href: `/topics/${topicId}`, label: 'Overview', icon: FileText },
    { href: `/topics/${topicId}/qa`, label: 'Q&A', icon: MessageSquare },
    { href: `/topics/${topicId}/flashcards`, label: 'Flashcards', icon: Brain },
  ];

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-80 max-w-[90vw] bg-white border-r border-gray-200 z-50 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-auto lg:h-screen lg:flex-shrink-0 safe-area-inset smooth-scroll ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 lg:hidden">
          <h2 className="text-lg font-semibold text-gray-900">Navigation</h2>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onClose}
            className="touch-target"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex flex-col h-full lg:h-screen lg:pt-16 lg:pb-0">
          {/* Main navigation */}
          <div className="p-4 border-b border-gray-200">
            <Link
              href="/dashboard"
              className={`flex items-center space-x-3 px-3 py-3 rounded-md text-sm font-medium transition-colors touch-target ${
                isActiveLink('/dashboard')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100 active:bg-gray-200'
              }`}
              onClick={onClose}
            >
              <Home className="h-5 w-5 flex-shrink-0" />
              <span>Dashboard</span>
            </Link>
          </div>

          {/* Topics section */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-4">
              {/* Topics header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                  Study Topics
                </h3>
                <Link href="/dashboard">
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={onClose}
                    className="touch-target"
                    aria-label="Add new topic"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </Link>
              </div>

              {/* Search topics */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 pointer-events-none" />
                <Input
                  type="text"
                  placeholder="Search topics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 text-sm h-11 touch-target"
                />
              </div>

              {/* Topics list */}
              {isLoading ? (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500">Loading topics...</p>
                </div>
              ) : filteredTopics.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500">
                    {topics.length === 0 ? 'No topics yet' : 'No topics match your search'}
                  </p>
                </div>
              ) : (
                <div className="space-y-1">
                  {filteredTopics.map((topic) => {
                    const isExpanded = expandedTopics.has(topic.id);
                    const subPages = getTopicSubPages(topic.id);
                    const hasActiveSubPage = subPages.some(page => isActiveLink(page.href));

                    return (
                      <div key={topic.id}>
                        {/* Topic header */}
                        <div
                          className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm cursor-pointer transition-colors ${
                            isActiveLink(`/topics/${topic.id}`) && !hasActiveSubPage
                              ? 'bg-blue-100 text-blue-700'
                              : 'text-gray-700 hover:bg-gray-100'
                          }`}
                        >
                          <button
                            onClick={() => toggleTopicExpansion(topic.id)}
                            className="flex-shrink-0"
                          >
                            {isExpanded ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronRight className="h-4 w-4" />
                            )}
                          </button>
                          
                          <BookOpen className="h-4 w-4 flex-shrink-0" />
                          
                          <Link
                            href={`/topics/${topic.id}`}
                            className="flex-1 truncate"
                            onClick={onClose}
                            title={topic.title}
                          >
                            {topic.title}
                          </Link>
                        </div>

                        {/* Topic sub-pages */}
                        {isExpanded && (
                          <div className="ml-6 mt-1 space-y-1">
                            {subPages.map((page) => (
                              <Link
                                key={page.href}
                                href={page.href}
                                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm transition-colors ${
                                  isActiveLink(page.href)
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                }`}
                                onClick={onClose}
                              >
                                <page.icon className="h-4 w-4" />
                                <span>{page.label}</span>
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}