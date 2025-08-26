import * as React from 'react'
import { cn } from '@/lib/utils'
import { 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  XCircle, 
  Info,
  Loader2
} from 'lucide-react'

interface StatusMessageProps extends React.HTMLAttributes<HTMLDivElement> {
  status: 'success' | 'error' | 'warning' | 'info' | 'loading' | 'pending'
  title?: string
  message: string
  showIcon?: boolean
  dismissible?: boolean
  onDismiss?: () => void
}

const statusConfig = {
  success: {
    icon: CheckCircle,
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    textColor: 'text-green-800',
    iconColor: 'text-green-600'
  },
  error: {
    icon: XCircle,
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-800',
    iconColor: 'text-red-600'
  },
  warning: {
    icon: AlertCircle,
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    textColor: 'text-yellow-800',
    iconColor: 'text-yellow-600'
  },
  info: {
    icon: Info,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-800',
    iconColor: 'text-blue-600'
  },
  loading: {
    icon: Loader2,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-800',
    iconColor: 'text-blue-600'
  },
  pending: {
    icon: Clock,
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    textColor: 'text-gray-800',
    iconColor: 'text-gray-600'
  }
}

const StatusMessage = React.forwardRef<HTMLDivElement, StatusMessageProps>(
  ({ 
    className, 
    status, 
    title, 
    message, 
    showIcon = true, 
    dismissible = false,
    onDismiss,
    ...props 
  }, ref) => {
    const config = statusConfig[status]
    const Icon = config.icon
    const isAnimated = status === 'loading'

    return (
      <div
        ref={ref}
        className={cn(
          'p-4 rounded-lg border',
          config.bgColor,
          config.borderColor,
          className
        )}
        {...props}
      >
        <div className="flex items-start gap-3">
          {showIcon && (
            <Icon 
              className={cn(
                'h-5 w-5 flex-shrink-0 mt-0.5',
                config.iconColor,
                isAnimated && 'animate-spin'
              )}
            />
          )}
          
          <div className="flex-1 min-w-0">
            {title && (
              <h4 className={cn('font-medium mb-1', config.textColor)}>
                {title}
              </h4>
            )}
            <p className={cn('text-sm', config.textColor)}>
              {message}
            </p>
          </div>

          {dismissible && onDismiss && (
            <button
              onClick={onDismiss}
              className={cn(
                'flex-shrink-0 p-1 rounded-md hover:bg-black hover:bg-opacity-10',
                config.textColor
              )}
            >
              <XCircle className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    )
  }
)
StatusMessage.displayName = 'StatusMessage'

export { StatusMessage }