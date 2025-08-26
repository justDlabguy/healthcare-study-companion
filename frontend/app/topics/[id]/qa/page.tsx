'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { topicsApi, documentsApi, type Topic, type Document } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useToastUtils } from '@/lib/toast-utils';
import { QAInterface } from '@/components/qa/qa-interface';
import { Loader2 } from 'lucide-react';

export default function QAPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const { showError } = useToastUtils();
  
  const topicId = parseInt(params.id as string);
  
  // State
  const [topic, setTopic] = useState<Topic | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);
  
  // Load topic and documents
  useEffect(() => {
    if (isAuthenticated && topicId) {
      loadData();
    }
  }, [isAuthenticated, topicId]);
  
  const loadData = async () => {
    try {
      setIsLoading(true);
      const [topicData, documentsData] = await Promise.all([
        topicsApi.getTopic(topicId),
        documentsApi.getDocuments(topicId).catch(() => [])
      ]);
      
      setTopic(topicData);
      setDocuments(documentsData);
    } catch (error) {
      console.error('Failed to load data:', error);
      showError('Error', 'Failed to load topic data');
    } finally {
      setIsLoading(false);
    }
  };
  
  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading Q&A interface...</p>
        </div>
      </div>
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
      {/* Q&A Interface */}
      <QAInterface
        topicId={topicId}
        topicTitle={topic.title}
        hasDocuments={documents.length > 0}
      />
    </div>
  );
}