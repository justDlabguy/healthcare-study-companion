import * as React from 'react'
import { cn } from '@/lib/utils'
import { Progress } from './progress'
import { StatusMessage } from './status-message'
import { Button } from './button'
import { 
  FileText, 
  Upload, 
  X, 
  CheckCircle, 
  AlertCircle,
  Loader2
} from 'lucide-react'

export interface FileUploadItem {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error'
  error?: string
  result?: any
}

interface FileUploadProgressProps {
  files: FileUploadItem[]
  onRemoveFile?: (fileId: string) => void
  onRetryFile?: (fileId: string) => void
  className?: string
}

const FileUploadProgress = React.forwardRef<HTMLDivElement, FileUploadProgressProps>(
  ({ className, files, onRemoveFile, onRetryFile, ...props }, ref) => {
    const getStatusIcon = (status: FileUploadItem['status']) => {
      switch (status) {
        case 'pending':
          return <Upload className="h-4 w-4 text-gray-500" />
        case 'uploading':
          return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
        case 'processing':
          return <Loader2 className="h-4 w-4 text-yellow-600 animate-spin" />
        case 'completed':
          return <CheckCircle className="h-4 w-4 text-green-600" />
        case 'error':
          return <AlertCircle className="h-4 w-4 text-red-600" />
        default:
          return <FileText className="h-4 w-4 text-gray-500" />
      }
    }

    const getStatusText = (status: FileUploadItem['status']) => {
      switch (status) {
        case 'pending':
          return 'Pending'
        case 'uploading':
          return 'Uploading'
        case 'processing':
          return 'Processing'
        case 'completed':
          return 'Completed'
        case 'error':
          return 'Error'
        default:
          return 'Unknown'
      }
    }

    const getProgressVariant = (status: FileUploadItem['status']) => {
      switch (status) {
        case 'completed':
          return 'success'
        case 'error':
          return 'error'
        case 'processing':
          return 'warning'
        default:
          return 'default'
      }
    }

    const formatFileSize = (bytes: number) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    if (files.length === 0) {
      return null
    }

    return (
      <div ref={ref} className={cn('space-y-3', className)} {...props}>
        {files.map((fileItem) => (
          <div
            key={fileItem.id}
            className="p-4 border rounded-lg bg-white shadow-sm"
          >
            {/* File Header */}
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <FileText className="h-5 w-5 text-gray-500 flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <h4 className="font-medium text-gray-900 truncate">
                    {fileItem.file.name}
                  </h4>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(fileItem.file.size)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2 flex-shrink-0">
                <div className="flex items-center gap-1">
                  {getStatusIcon(fileItem.status)}
                  <span className="text-sm text-gray-600">
                    {getStatusText(fileItem.status)}
                  </span>
                </div>
                
                {onRemoveFile && (fileItem.status === 'pending' || fileItem.status === 'error') && (
                  <Button
                    onClick={() => onRemoveFile(fileItem.id)}
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 text-gray-500 hover:text-red-600"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            {(fileItem.status === 'uploading' || fileItem.status === 'processing' || fileItem.status === 'completed') && (
              <div className="mb-3">
                <Progress
                  value={fileItem.progress}
                  variant={getProgressVariant(fileItem.status)}
                  showLabel
                  label={
                    fileItem.status === 'uploading' ? 'Uploading' :
                    fileItem.status === 'processing' ? 'Processing' :
                    'Complete'
                  }
                />
              </div>
            )}

            {/* Error Message */}
            {fileItem.status === 'error' && fileItem.error && (
              <div className="mb-3">
                <StatusMessage
                  status="error"
                  message={fileItem.error}
                  showIcon={false}
                />
              </div>
            )}

            {/* Success Message */}
            {fileItem.status === 'completed' && (
              <div className="mb-3">
                <StatusMessage
                  status="success"
                  message="File uploaded and processed successfully"
                  showIcon={false}
                />
              </div>
            )}

            {/* Processing Message */}
            {fileItem.status === 'processing' && (
              <div className="mb-3">
                <StatusMessage
                  status="loading"
                  message="Processing document for search and Q&A..."
                  showIcon={false}
                />
              </div>
            )}

            {/* Retry Button */}
            {fileItem.status === 'error' && onRetryFile && (
              <div className="flex justify-end">
                <Button
                  onClick={() => onRetryFile(fileItem.id)}
                  variant="outline"
                  size="sm"
                  className="text-blue-600 hover:text-blue-700"
                >
                  Retry Upload
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }
)
FileUploadProgress.displayName = 'FileUploadProgress'

export { FileUploadProgress }