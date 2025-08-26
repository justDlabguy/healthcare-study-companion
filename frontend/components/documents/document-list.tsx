'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { useConfirmDialog } from '@/hooks/use-confirm-dialog';
import { 
  FileText, 
  Trash2, 
  RefreshCw, 
  CheckCircle, 
  Clock, 
  AlertCircle
} from 'lucide-react';
import { Document } from '@/lib/api';

interface DocumentListProps {
  documents: Document[];
  topicId: number;
  onDocumentDeleted: (documentId: number) => void;
  onDocumentReprocessed: (document: Document) => void;
}

export function DocumentList({ 
  documents, 
  topicId, 
  onDocumentDeleted, 
  onDocumentReprocessed 
}: DocumentListProps) {
  const { toast } = useToast();
  const { showConfirmDialog } = useConfirmDialog();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PROCESSED':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'PROCESSING':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'ERROR':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PROCESSED':
        return 'bg-green-100 text-green-800';
      case 'PROCESSING':
        return 'bg-yellow-100 text-yellow-800';
      case 'ERROR':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDeleteDocument = async (documentId: number, filename: string) => {
    const confirmed = await showConfirmDialog({
      title: 'Delete Document',
      message: `Are you sure you want to delete "${filename}"? This action cannot be undone and will remove all associated Q&A history and flashcards.`
    });

    if (!confirmed) return;

    try {
      const { documentsApi } = await import('@/lib/api');
      await documentsApi.deleteDocument(topicId, documentId);
      onDocumentDeleted(documentId);
      
      toast({
        title: 'Document Deleted',
        description: `${filename} has been deleted successfully.`
      });
    } catch (error) {
      console.error('Failed to delete document:', error);
      toast({
        title: 'Delete Failed',
        description: 'Failed to delete document. Please try again.',
        variant: 'destructive'
      });
    }
  };

  const handleReprocessDocument = async (document: Document) => {
    try {
      const { documentsApi } = await import('@/lib/api');
      const reprocessedDocument = await documentsApi.reprocessDocument(document.id);
      onDocumentReprocessed(reprocessedDocument);
      
      toast({
        title: 'Reprocessing Started',
        description: `${document.filename} is being reprocessed.`
      });
    } catch (error) {
      console.error('Failed to reprocess document:', error);
      toast({
        title: 'Reprocess Failed',
        description: 'Failed to reprocess document. Please try again.',
        variant: 'destructive'
      });
    }
  };

  if (documents.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No documents uploaded</h3>
            <p className="text-gray-600">
              Upload your first document to start asking questions and generating flashcards.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Documents ({documents.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {documents.map((document) => (
            <div
              key={document.id}
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              {/* Header with filename and status */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <FileText className="h-5 w-5 text-gray-500 flex-shrink-0" />
                  <h4 className="font-medium text-gray-900 truncate">
                    {document.filename}
                  </h4>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {getStatusIcon(document.status)}
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(document.status)}`}>
                    {document.status}
                  </span>
                </div>
              </div>
              
              {/* Document metadata */}
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-sm text-gray-500 mb-3">
                <span>
                  Uploaded {new Date(document.created_at).toLocaleDateString()}
                </span>
                {document.file_size && (
                  <span>{formatFileSize(document.file_size)}</span>
                )}
              </div>

              {/* Error message */}
              {document.error_message && (
                <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  <strong>Error:</strong> {document.error_message}
                </div>
              )}

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row gap-2">
                {document.status === 'ERROR' && (
                  <Button
                    onClick={() => handleReprocessDocument(document)}
                    variant="outline"
                    size="sm"
                    className="text-blue-600 hover:text-blue-700 w-full sm:w-auto"
                  >
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Retry
                  </Button>
                )}
                
                <Button
                  onClick={() => handleDeleteDocument(document.id, document.filename)}
                  variant="outline"
                  size="sm"
                  className="text-red-600 hover:text-red-700 w-full sm:w-auto"
                >
                  <Trash2 className="h-4 w-4 mr-1 sm:mr-0" />
                  <span className="sm:hidden">Delete</span>
                </Button>
              </div>
            </div>
          ))}
        </div>

        {documents.some(doc => doc.status === 'PROCESSING') && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 text-blue-800">
              <Clock className="h-4 w-4" />
              <span className="text-sm font-medium">
                Documents are being processed. This may take a few minutes.
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}