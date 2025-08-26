import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Topic } from '@/lib/api';
import { useConfirmDialog } from '@/hooks/use-confirm-dialog';
import { MoreVertical, Edit, Trash2, FileText, MessageSquare, Brain } from 'lucide-react';

interface TopicCardProps {
  topic: Topic;
  onEdit: (topic: Topic) => void;
  onDelete: (topicId: number) => void;
}

export function TopicCard({ topic, onEdit, onDelete }: TopicCardProps) {
  const [showActions, setShowActions] = useState(false);
  const { showConfirmDialog } = useConfirmDialog();

  const handleDelete = async () => {
    const confirmed = await showConfirmDialog({
      title: 'Delete Topic',
      message: `Are you sure you want to delete "${topic.title}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
    });

    if (confirmed) {
      onDelete(topic.id);
    }
  };

  return (
    <Card className="relative group hover:shadow-md transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base sm:text-lg line-clamp-2 break-words">
              {topic.title}
            </CardTitle>
            <CardDescription className="mt-1 line-clamp-2 text-sm">
              {topic.description || 'No description provided'}
            </CardDescription>
          </div>
          <div className="relative flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              className="opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity touch-target"
              onClick={() => setShowActions(!showActions)}
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
            {showActions && (
              <>
                {/* Mobile backdrop */}
                <div 
                  className="fixed inset-0 z-40 sm:hidden" 
                  onClick={() => setShowActions(false)}
                />
                <div className="absolute right-0 top-8 bg-white border rounded-md shadow-lg z-50 min-w-[140px]">
                  <button
                    onClick={() => {
                      onEdit(topic);
                      setShowActions(false);
                    }}
                    className="flex items-center gap-2 w-full px-3 py-3 text-sm hover:bg-gray-50 text-left touch-target"
                  >
                    <Edit className="h-4 w-4" />
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      handleDelete();
                      setShowActions(false);
                    }}
                    className="flex items-center gap-2 w-full px-3 py-3 text-sm hover:bg-gray-50 text-left text-red-600 touch-target"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0 space-y-4">
        <div className="text-xs sm:text-sm text-gray-500">
          <span>Created {new Date(topic.created_at).toLocaleDateString()}</span>
        </div>
        
        <div className="space-y-2">
          <Link href={`/topics/${topic.id}` as any} className="block">
            <Button variant="outline" size="sm" className="w-full touch-target">
              <FileText className="h-4 w-4 mr-2" />
              <span className="hidden xs:inline">View Details</span>
              <span className="xs:hidden">Details</span>
            </Button>
          </Link>
          
          <div className="grid grid-cols-2 gap-2">
            <Link href={`/topics/${topic.id}/qa` as any}>
              <Button variant="ghost" size="sm" className="w-full touch-target">
                <MessageSquare className="h-4 w-4 mr-1 sm:mr-2" />
                <span className="text-xs sm:text-sm">Q&A</span>
              </Button>
            </Link>
            <Link href={`/topics/${topic.id}/flashcards` as any}>
              <Button variant="ghost" size="sm" className="w-full touch-target">
                <Brain className="h-4 w-4 mr-1 sm:mr-2" />
                <span className="text-xs sm:text-sm">Cards</span>
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}