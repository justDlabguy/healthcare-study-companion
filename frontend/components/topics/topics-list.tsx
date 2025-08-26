import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LoadingState } from '@/components/ui/loading-state';
import { StatusMessage } from '@/components/ui/status-message';
import { TopicCard } from './topic-card';
import { TopicForm } from './topic-form';
import { Topic, topicsApi, CreateTopicRequest, UpdateTopicRequest } from '@/lib/api';
import { Plus, Search } from 'lucide-react';

export function TopicsList() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [filteredTopics, setFilteredTopics] = useState<Topic[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Load topics on component mount
  useEffect(() => {
    loadTopics();
  }, []);

  // Filter topics based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredTopics(topics);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = topics.filter(
        topic =>
          topic.title.toLowerCase().includes(query) ||
          (topic.description && topic.description.toLowerCase().includes(query))
      );
      setFilteredTopics(filtered);
    }
  }, [topics, searchQuery]);

  const loadTopics = async () => {
    try {
      setIsLoading(true);
      setError('');
      const data = await topicsApi.getTopics();
      setTopics(data);
    } catch (error: any) {
      console.error('Failed to load topics:', error);
      let errorMessage = 'Unable to load topics. Please try again.';
      
      if (error.response?.status === 401) {
        errorMessage = 'Your session has expired. Please log in again.';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error. Please try again in a few moments.';
      } else if (!error.response) {
        errorMessage = 'Network error. Please check your internet connection.';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTopic = async (data: CreateTopicRequest) => {
    setIsSubmitting(true);
    try {
      const newTopic = await topicsApi.createTopic(data);
      setTopics(prev => [newTopic, ...prev]);
      setShowForm(false);
    } catch (error) {
      throw error; // Let the form handle the error
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateTopic = async (data: CreateTopicRequest) => {
    if (!editingTopic) return;
    
    setIsSubmitting(true);
    try {
      // Convert CreateTopicRequest to UpdateTopicRequest
      const updateData: UpdateTopicRequest = {
        title: data.title,
        description: data.description,
      };
      const updatedTopic = await topicsApi.updateTopic(editingTopic.id, updateData);
      setTopics(prev => prev.map(topic => 
        topic.id === editingTopic.id ? updatedTopic : topic
      ));
      setEditingTopic(null);
      setShowForm(false);
    } catch (error) {
      throw error; // Let the form handle the error
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTopic = async (topicId: number) => {
    try {
      await topicsApi.deleteTopic(topicId);
      setTopics(prev => prev.filter(topic => topic.id !== topicId));
    } catch (error: any) {
      console.error('Failed to delete topic:', error);
      let errorMessage = 'Unable to delete topic. Please try again.';
      
      if (error.response?.status === 401) {
        errorMessage = 'Your session has expired. Please log in again.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to delete this topic.';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error. Please try again in a few moments.';
      } else if (!error.response) {
        errorMessage = 'Network error. Please check your internet connection.';
      }
      
      setError(errorMessage);
    }
  };

  const handleEditTopic = (topic: Topic) => {
    setEditingTopic(topic);
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTopic(null);
  };

  if (showForm) {
    return (
      <div className="py-8">
        <TopicForm
          topic={editingTopic || undefined}
          onSubmit={editingTopic ? handleUpdateTopic : handleCreateTopic}
          onCancel={handleCancelForm}
          isLoading={isSubmitting}
        />
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Study Topics</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            Organize your study materials by topic
          </p>
        </div>
        <div className="flex-shrink-0">
          <Button 
            onClick={() => setShowForm(true)}
            className="w-full sm:w-auto touch-target"
            size="default"
          >
            <Plus className="h-4 w-4 mr-2" />
            <span className="hidden xs:inline">New Topic</span>
            <span className="xs:hidden">New</span>
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 pointer-events-none" />
        <Input
          type="text"
          placeholder="Search topics..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 h-11 touch-target"
        />
      </div>

      {/* Error Message */}
      {error && (
        <StatusMessage
          status="error"
          message={error}
          dismissible
          onDismiss={() => setError('')}
        />
      )}

      {/* Loading State */}
      {isLoading && (
        <LoadingState 
          message="Loading your study topics..." 
          size="lg"
          variant="primary"
        />
      )}

      {/* Topics Grid */}
      {!isLoading && (
        <>
          {filteredTopics.length === 0 ? (
            <div className="text-center py-12">
              {topics.length === 0 ? (
                <div>
                  <p className="text-gray-600 mb-4">No topics yet</p>
                  <Button onClick={() => setShowForm(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Topic
                  </Button>
                </div>
              ) : (
                <p className="text-gray-600">
                  No topics match your search query
                </p>
              )}
            </div>
          ) : (
            <div className="grid gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {filteredTopics.map((topic) => (
                <TopicCard
                  key={topic.id}
                  topic={topic}
                  onEdit={handleEditTopic}
                  onDelete={handleDeleteTopic}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}