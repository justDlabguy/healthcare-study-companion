import * as React from 'react'
import { cn } from '@/lib/utils'
import { Progress } from './progress'
import { StatusMessage } from './status-message'
import { Button } from './button'
import { 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  XCircle, 
  Loader2,
  X,
  RefreshCw
} from 'lucide-react'

export interface BackgroundTask {
  id: string
  type: 'upload' | 'processing' | 'generation' | 'analysis' | 'other'
  title: string
  description?: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress?: number
  startTime?: Date
  endTime?: Date
  error?: string
  result?: any
}

interface BackgroundTaskStatusProps extends React.HTMLAttributes<HTMLDivElement> {
  tasks: BackgroundTask[]
  onRetryTask?: (taskId: string) => void
  onCancelTask?: (taskId: string) => void
  onDismissTask?: (taskId: string) => void
  showCompleted?: boolean
  maxVisible?: number
}

const BackgroundTaskStatus = React.forwardRef<HTMLDivElement, BackgroundTaskStatusProps>(
  ({ 
    className,
    tasks,
    onRetryTask,
    onCancelTask,
    onDismissTask,
    showCompleted = true,
    maxVisible = 5,
    ...props 
  }, ref) => {
    const visibleTasks = React.useMemo(() => {
      let filtered = showCompleted 
        ? tasks 
        : tasks.filter(task => task.status !== 'completed')
      
      return filtered.slice(0, maxVisible)
    }, [tasks, showCompleted, maxVisible])

    const getTaskIcon = (task: BackgroundTask) => {
      switch (task.status) {
        case 'pending':
          return <Clock className="h-4 w-4 text-gray-500" />
        case 'running':
          return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
        case 'completed':
          return <CheckCircle className="h-4 w-4 text-green-600" />
        case 'failed':
          return <XCircle className="h-4 w-4 text-red-600" />
        case 'cancelled':
          return <AlertCircle className="h-4 w-4 text-gray-600" />
        default:
          return <Clock className="h-4 w-4 text-gray-500" />
      }
    }

    const getTaskStatusText = (task: BackgroundTask) => {
      switch (task.status) {
        case 'pending':
          return 'Pending'
        case 'running':
          return 'Running'
        case 'completed':
          return 'Completed'
        case 'failed':
          return 'Failed'
        case 'cancelled':
          return 'Cancelled'
        default:
          return 'Unknown'
      }
    }

    const getProgressVariant = (status: BackgroundTask['status']) => {
      switch (status) {
        case 'completed':
          return 'success'
        case 'failed':
          return 'error'
        case 'cancelled':
          return 'warning'
        default:
          return 'default'
      }
    }

    const formatDuration = (startTime?: Date, endTime?: Date) => {
      if (!startTime) return null
      
      const end = endTime || new Date()
      const duration = Math.floor((end.getTime() - startTime.getTime()) / 1000)
      
      if (duration < 60) return `${duration}s`
      if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`
      return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`
    }

    if (visibleTasks.length === 0) {
      return null
    }

    return (
      <div ref={ref} className={cn('space-y-3', className)} {...props}>
        {visibleTasks.map((task) => (
          <div
            key={task.id}
            className="bg-white border rounded-lg p-4 shadow-sm"
          >
            {/* Task Header */}
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-3 min-w-0 flex-1">
                {getTaskIcon(task)}
                <div className="min-w-0 flex-1">
                  <h4 className="font-medium text-gray-900 truncate">
                    {task.title}
                  </h4>
                  {task.description && (
                    <p className="text-sm text-gray-600 truncate">
                      {task.description}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-sm text-gray-600">
                  {getTaskStatusText(task)}
                </span>
                
                {onDismissTask && (task.status === 'completed' || task.status === 'failed') && (
                  <Button
                    onClick={() => onDismissTask(task.id)}
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 text-gray-500 hover:text-gray-700"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            {task.status === 'running' && typeof task.progress === 'number' && (
              <div className="mb-3">
                <Progress
                  value={task.progress}
                  variant={getProgressVariant(task.status)}
                  showLabel
                  label="Progress"
                />
              </div>
            )}

            {/* Error Message */}
            {task.status === 'failed' && task.error && (
              <div className="mb-3">
                <StatusMessage
                  status="error"
                  message={task.error}
                  showIcon={false}
                />
              </div>
            )}

            {/* Success Message */}
            {task.status === 'completed' && (
              <div className="mb-3">
                <StatusMessage
                  status="success"
                  message="Task completed successfully"
                  showIcon={false}
                />
              </div>
            )}

            {/* Task Footer */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center gap-4">
                {task.startTime && (
                  <span>
                    Started: {task.startTime.toLocaleTimeString()}
                  </span>
                )}
                {formatDuration(task.startTime, task.endTime) && (
                  <span>
                    Duration: {formatDuration(task.startTime, task.endTime)}
                  </span>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                {task.status === 'failed' && onRetryTask && (
                  <Button
                    onClick={() => onRetryTask(task.id)}
                    variant="outline"
                    size="sm"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Retry
                  </Button>
                )}
                
                {task.status === 'running' && onCancelTask && (
                  <Button
                    onClick={() => onCancelTask(task.id)}
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Show more indicator */}
        {tasks.length > maxVisible && (
          <div className="text-center">
            <p className="text-sm text-gray-500">
              Showing {maxVisible} of {tasks.length} tasks
            </p>
          </div>
        )}
      </div>
    )
  }
)
BackgroundTaskStatus.displayName = 'BackgroundTaskStatus'

export { BackgroundTaskStatus }