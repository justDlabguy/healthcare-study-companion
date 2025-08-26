'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { topicsApi, documentsApi, type Topic, type Document } from '@/lib/api';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToastUtils } from '@/lib/toast-utils';
import { DocumentUpload } from '@/components/documents/document-upload';
import { DocumentList } from '@/components/documents/document-list';
import { QAInterface } from '@/components/qa/qa-interface';
import { FlashcardInterface } from '@/components/flashcards/flashcard-interface';
import { SearchInterface } from '@/components/search/search-interface';
import { Loader2 } from 'lucide-react';
import { LoadingState } from '@/components/ui/loading-state';
import { StatusMessage } from '@/components/ui/status-message';

export default function TopicDetailPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const { showError, showSuccess, showInfo } = useToastUtils();
  
  const topicId = parseInt(params.id as string);
  
  // State
  const [topic, setTopic] = useState<Topic | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState<'documents' | 'qa' | 'flashcards' | 'search'>('documents');
  const [editMode, setEditMode] = useState(false);
  const [editForm, setEditForm] = useState({ title: '', description: '' });
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);
  
  // Load topic and documents
  useEffect(() => {
    if (isAuthenticated && topicId) {
      loadTopicData();
    }
  }, [isAuthenticated, topicId]);
  
  const loadTopicData = async () => {
    try {
      setIsLoading(true);
      const [topicData, documentsData] = await Promise.all([
        topicsApi.getTopic(topicId),
        documentsApi.getDocuments(topicId).catch(() => []) // Handle case where no documents exist
      ]);
      
      setTopic(topicData);
      setDocuments(documentsData);
      setEditForm({ title: topicData.title, description: topicData.description });
    } catch (error) {
      console.error('Failed to load topic data:', error);
      showError('Error', 'Failed to load topic data');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleEditTopic = async () => {
    if (!topic) return;
    
    try {
      const updatedTopic = await topicsApi.updateTopic(topic.id, editForm);
      setTopic(updatedTopic);
      setEditMode(false);
      showSuccess('Success', 'Topic updated successfully');
    } catch (error) {
      console.error('Failed to update topic:', error);
      showError('Error', 'Failed to update topic');
    }
  };

  const handleUploadSuccess = (document: Document) => {
    setDocuments(prev => [...prev, document]);
  };

  const handleDocumentDeleted = (documentId: number) => {
    setDocuments(prev => prev.filter(doc => doc.id !== documentId));
  };

  const handleDocumentReprocessed = (document: Document) => {
    setDocuments(prev => prev.map(doc => 
      doc.id === document.id ? document : doc
    ));
  };
  
  if (authLoading || isLoading) {
    return (
      <LoadingState 
        message="Loading topic details..." 
        size="xl"
        variant="primary"
        fullScreen
      />
    );
  }
  
  if (!topic) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Topic Not Found</h1>
          <p className="text-gray-600 mb-4">The topic you're looking for doesn't exist.</p>
          <Button onClick={() => router.push('/dashboard')}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }
  
  return (
    <div>
      {/* Topic Header */}
      <div className="mb-4 sm:mb-6">
        <Card>
          <CardHeader className="p-4 sm:p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="flex-1 min-w-0">
                {editMode ? (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="title" className="text-sm font-medium">Topic Title</Label>
                      <Input
                        id="title"
                        value={editForm.title}
                        onChange={(e) => setEditForm(prev => ({ ...prev, title: e.target.value }))}
                        placeholder="Enter topic title"
                        className="w-full mt-1 touch-target"
                      />
                    </div>
                    <div>
                      <Label htmlFor="description" className="text-sm font-medium">Description</Label>
                      <Input
                        id="description"
                        value={editForm.description}
                        onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Enter topic description"
                        className="w-full mt-1 touch-target"
                      />
                    </div>
                    <div className="flex flex-col xs:flex-row gap-2">
                      <Button 
                        onClick={handleEditTopic} 
                        size="sm" 
                        className="w-full xs:w-auto touch-target"
                      >
                        Save Changes
                      </Button>
                      <Button 
                        onClick={() => {
                          setEditMode(false);
                          setEditForm({ title: topic.title, description: topic.description });
                        }} 
                        variant="outline" 
                        size="sm"
                        className="w-full xs:w-auto touch-target"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="min-w-0">
                    <CardTitle className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 break-words leading-tight">
                      {topic.title}
                    </CardTitle>
                    <p className="text-gray-600 mt-2 text-sm sm:text-base break-words leading-relaxed">
                      {topic.description}
                    </p>
                  </div>
                )}
              </div>
              
              {!editMode && (
                <div className="flex-shrink-0">
                  <Button 
                    onClick={() => setEditMode(true)} 
                    variant="outline" 
                    size="sm"
                    className="w-full sm:w-auto touch-target"
                  >
                    <span className="hidden xs:inline">Edit Topic</span>
                    <span className="xs:hidden">Edit</span>
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>
        </Card>
      </div>
      
      {/* Navigation Tabs */}
      <div className="mb-4 sm:mb-6">
        <div className="border-b border-gray-200 overflow-x-auto smooth-scroll">
          <nav className="-mb-px flex space-x-1 sm:space-x-4 lg:space-x-8 min-w-max px-1">
            <button
              onClick={() => setActiveTab('documents')}
              className={`py-3 px-3 sm:px-4 border-b-2 font-medium text-sm whitespace-nowrap transition-colors touch-target ${
                activeTab === 'documents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 active:text-gray-800'
              }`}
            >
              <span className="hidden sm:inline">Documents ({documents.length})</span>
              <span className="sm:hidden">Docs ({documents.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('qa')}
              className={`py-3 px-3 sm:px-4 border-b-2 font-medium text-sm whitespace-nowrap transition-colors touch-target ${
                activeTab === 'qa'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 active:text-gray-800'
              }`}
            >
              Q&A
            </button>
            <button
              onClick={() => setActiveTab('flashcards')}
              className={`py-3 px-3 sm:px-4 border-b-2 font-medium text-sm whitespace-nowrap transition-colors touch-target ${
                activeTab === 'flashcards'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 active:text-gray-800'
              }`}
            >
              <span className="hidden xs:inline">Flashcards</span>
              <span className="xs:hidden">Cards</span>
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`py-3 px-3 sm:px-4 border-b-2 font-medium text-sm whitespace-nowrap transition-colors touch-target ${
                activeTab === 'search'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 active:text-gray-800'
              }`}
            >
              Search
            </button>
          </nav>
        </div>
      </div>
      
      {/* Tab Content */}
      {activeTab === 'documents' && (
        <div className="space-y-6">
          <DocumentUpload
            topicId={topicId}
            onUploadSuccess={handleUploadSuccess}
            isUploading={isUploading}
            onUploadStart={() => setIsUploading(true)}
            onUploadEnd={() => setIsUploading(false)}
          />
          
          <DocumentList
            documents={documents}
            topicId={topicId}
            onDocumentDeleted={handleDocumentDeleted}
            onDocumentReprocessed={handleDocumentReprocessed}
          />
        </div>
      )}
      
      {activeTab === 'qa' && (
        <QAInterface
          topicId={topicId}
          topicTitle={topic.title}
          hasDocuments={documents.length > 0}
        />
      )}
      
      {activeTab === 'flashcards' && (
        <FlashcardInterface
          topicId={topicId}
          topicTitle={topic.title}
          hasDocuments={documents.length > 0}
        />
      )}
      
      {activeTab === 'search' && (
        <div className="space-y-6">
          <StatusMessage
            status="info"
            title="Semantic Search"
            message="Search through your uploaded documents using AI-powered semantic search. Find relevant content even when you don't remember the exact keywords."
          />
          
          <SearchInterface
            topicId={topicId}
            documents={documents}
            onResultClick={(result) => {
              showInfo(
                "Search Result",
                `Found in ${result.document_filename} (${(result.score * 100).toFixed(0)}% relevance)`
              );
            }}
          />
        </div>
      )}
    </div>
  );
}