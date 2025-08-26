import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Topic, CreateTopicRequest, UpdateTopicRequest } from '@/lib/api';

interface TopicFormProps {
  topic?: Topic;
  onSubmit: (data: CreateTopicRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function TopicForm({ topic, onSubmit, onCancel, isLoading = false }: TopicFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (topic) {
      setTitle(topic.title);
      setDescription(topic.description || '');
    }
  }, [topic]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Topic title is required');
      return;
    }

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim(),
      });
    } catch (error: any) {
      console.error('Form submission error:', error);
      
      // Handle different error response formats with user-friendly messages
      let errorMessage = 'Unable to save topic. Please check your connection and try again.';
      
      if (error.response?.status === 401) {
        errorMessage = 'Your session has expired. Please log in again.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to perform this action.';
      } else if (error.response?.status === 400) {
        // Handle validation errors
        if (error.response?.data?.detail) {
          const errorData = error.response.data;
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((err: any) => {
              // Convert technical field names to user-friendly names
              const fieldName = err.loc?.[1] === 'title' ? 'Topic title' : 'Description';
              return `${fieldName}: ${err.msg}`;
            }).join(', ');
          } else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          }
        }
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error. Please try again in a few moments.';
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        errorMessage = 'Network error. Please check your internet connection.';
      }
      
      setError(errorMessage);
    }
  };

  return (
    <Card className="w-full max-w-lg mx-auto">
      <CardHeader className="p-4 sm:p-6">
        <CardTitle className="text-lg sm:text-xl">
          {topic ? 'Edit Topic' : 'Create New Topic'}
        </CardTitle>
        <CardDescription className="text-sm sm:text-base">
          {topic ? 'Update your topic details' : 'Add a new study topic to organize your materials'}
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4 sm:p-6 pt-0">
        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
              {typeof error === 'string' ? error : 'An error occurred. Please try again.'}
            </div>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="title" className="text-sm font-medium">Topic Title</Label>
            <Input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter topic title"
              required
              disabled={isLoading}
              className="touch-target"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium">Description</Label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter topic description (optional)"
              disabled={isLoading}
              className="flex min-h-[100px] sm:min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 touch-target resize-none"
              rows={4}
            />
          </div>
          
          <div className="flex flex-col xs:flex-row gap-3 pt-2">
            <Button 
              type="submit" 
              className="flex-1 touch-target" 
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : (topic ? 'Update Topic' : 'Create Topic')}
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 xs:flex-initial touch-target"
            >
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}