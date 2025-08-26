'use client';

import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { useErrorToast } from '@/hooks/use-error-toast';
import { useUploadRetry } from '@/hooks/use-retry';
import { FileUploadProgress, type FileUploadItem } from '@/components/ui/file-upload-progress';
import { StatusMessage } from '@/components/ui/status-message';
import { Upload, FileText, AlertCircle } from 'lucide-react';

interface DocumentUploadProps {
  topicId: number;
  onUploadSuccess: (document: any) => void;
  isUploading: boolean;
  onUploadStart: () => void;
  onUploadEnd: () => void;
}

export function DocumentUpload({ 
  topicId, 
  onUploadSuccess, 
  isUploading, 
  onUploadStart, 
  onUploadEnd 
}: DocumentUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadQueue, setUploadQueue] = useState<FileUploadItem[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const { showError, showSuccess } = useErrorToast();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const validateFile = (file: File): string | null => {
    // Validate file type
    const allowedTypes = ['application/pdf', 'text/plain'];
    const allowedExtensions = ['.pdf', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      return 'Only PDF and TXT files are supported.';
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      return 'File size must be less than 10MB.';
    }

    return null;
  };

  const addFileToQueue = (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      toast({
        title: 'Invalid File',
        description: validationError,
        variant: 'destructive'
      });
      return;
    }

    const fileItem: FileUploadItem = {
      id: `${Date.now()}-${Math.random()}`,
      file,
      progress: 0,
      status: 'pending'
    };

    setUploadQueue(prev => [...prev, fileItem]);
    
    // Start upload immediately
    uploadFile(fileItem);
  };

  const uploadFile = async (fileItem: FileUploadItem) => {
    try {
      onUploadStart();
      
      // Update status to uploading
      setUploadQueue(prev => prev.map(item => 
        item.id === fileItem.id 
          ? { ...item, status: 'uploading', progress: 0 }
          : item
      ));

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadQueue(prev => prev.map(item => {
          if (item.id === fileItem.id && item.status === 'uploading') {
            const newProgress = Math.min(item.progress + Math.random() * 20, 90);
            return { ...item, progress: newProgress };
          }
          return item;
        }));
      }, 200);

      // Import the API here to avoid circular dependencies
      const { documentsApi } = await import('@/lib/api');
      const uploadedDocument = await documentsApi.uploadDocument(topicId, fileItem.file);
      
      clearInterval(progressInterval);
      
      // Update to processing status
      setUploadQueue(prev => prev.map(item => 
        item.id === fileItem.id 
          ? { ...item, status: 'processing', progress: 95 }
          : item
      ));

      // Simulate processing time
      setTimeout(() => {
        setUploadQueue(prev => prev.map(item => 
          item.id === fileItem.id 
            ? { ...item, status: 'completed', progress: 100, result: uploadedDocument }
            : item
        ));

        onUploadSuccess(uploadedDocument);
        
        toast({
          title: 'Upload Successful',
          description: `${fileItem.file.name} has been uploaded and is being processed.`
        });

        // Remove completed file from queue after 3 seconds
        setTimeout(() => {
          setUploadQueue(prev => prev.filter(item => item.id !== fileItem.id));
        }, 3000);
      }, 1000);

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload failed:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Upload failed. Please try again.';
      
      setUploadQueue(prev => prev.map(item => 
        item.id === fileItem.id 
          ? { 
              ...item, 
              status: 'error', 
              progress: 0,
              error: errorMessage
            }
          : item
      ));

      showError(error, {
        title: 'Upload Failed',
        onRetry: () => uploadFile(fileItem)
      });
    } finally {
      onUploadEnd();
    }
  };

  const handleFileUpload = (file: File) => {
    addFileToQueue(file);
  };

  const removeFileFromQueue = (fileId: string) => {
    setUploadQueue(prev => prev.filter(item => item.id !== fileId));
  };

  const retryFileUpload = (fileId: string) => {
    const fileItem = uploadQueue.find(item => item.id === fileId);
    if (fileItem) {
      uploadFile(fileItem);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const hasActiveUploads = uploadQueue.some(item => 
    item.status === 'uploading' || item.status === 'processing'
  );

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-4 sm:p-8 text-center transition-colors ${
              dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            } ${hasActiveUploads ? 'opacity-50 pointer-events-none' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleFileSelect}
              accept=".pdf,.txt"
              disabled={hasActiveUploads}
              multiple
            />

            <div className="space-y-4">
              <div className="flex justify-center">
                {hasActiveUploads ? (
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                ) : (
                  <FileText className="h-12 w-12 text-gray-400" />
                )}
              </div>

              <div>
                <p className="text-base sm:text-lg font-medium text-gray-900 mb-2">
                  {hasActiveUploads ? 'Processing uploads...' : 'Drop files here or click to browse'}
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  Supports PDF and TXT files up to 10MB
                </p>
                
                {!hasActiveUploads && (
                  <Button onClick={openFileDialog} variant="outline" className="w-full sm:w-auto">
                    Choose Files
                  </Button>
                )}
              </div>

              <div className="flex items-center justify-center gap-2 text-xs text-gray-500 px-2">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                <span className="text-center">Documents will be automatically processed for Q&A and flashcards</span>
              </div>
            </div>
          </div>

          {/* Upload Progress */}
          {uploadQueue.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Upload Progress</h4>
              <FileUploadProgress
                files={uploadQueue}
                onRemoveFile={removeFileFromQueue}
                onRetryFile={retryFileUpload}
              />
            </div>
          )}

          {/* Status Messages */}
          {hasActiveUploads && (
            <div className="mt-4">
              <StatusMessage
                status="loading"
                message="Files are being uploaded and processed. This may take a few minutes depending on file size."
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}