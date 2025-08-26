import * as React from 'react'
import { cn } from '@/lib/utils'
import { Spinner } from './spinner'
import { Progress } from './progress'

interface LoadingOverlayProps extends React.HTMLAttributes<HTMLDivElement> {
  isVisible: boolean
  message?: string
  progress?: number
  showProgress?: boolean
  variant?: 'default' | 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  backdrop?: 'light' | 'dark' | 'blur'
  onClose?: () => void
}

const LoadingOverlay = React.forwardRef<HTMLDivElement, LoadingOverlayProps>(
  ({ 
    className,
    isVisible,
    message = 'Loading...',
    progress,
    showProgress = false,
    variant = 'primary',
    size = 'lg',
    backdrop = 'light',
    ...props 
  }, ref) => {
    if (!isVisible) return null

    const backdropClasses = {
      light: 'bg-white bg-opacity-75',
      dark: 'bg-black bg-opacity-50',
      blur: 'bg-white bg-opacity-75 backdrop-blur-sm'
    }

    return (
      <div
        ref={ref}
        className={cn(
          'fixed inset-0 z-50 flex items-center justify-center',
          backdropClasses[backdrop],
          className
        )}
        {...props}
      >
        <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
          <div className="text-center">
            <Spinner size={size} variant={variant} className="mb-4" />
            
            <h3 className={cn(
              'font-medium text-gray-900 mb-2',
              size === 'sm' && 'text-sm',
              size === 'md' && 'text-base',
              size === 'lg' && 'text-lg',
              size === 'xl' && 'text-xl'
            )}>
              {message}
            </h3>

            {showProgress && typeof progress === 'number' && (
              <div className="mt-4">
                <Progress
                  value={progress}
                  variant={variant === 'primary' ? 'default' : variant === 'secondary' ? 'default' : variant}
                  showLabel
                />
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }
)
LoadingOverlay.displayName = 'LoadingOverlay'

export { LoadingOverlay }