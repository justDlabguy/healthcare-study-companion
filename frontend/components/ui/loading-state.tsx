import * as React from 'react'
import { cn } from '@/lib/utils'
import { Spinner } from './spinner'

interface LoadingStateProps extends React.HTMLAttributes<HTMLDivElement> {
  message?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'primary' | 'secondary'
  fullScreen?: boolean
  compact?: boolean
  showSpinner?: boolean
}

const LoadingState = React.forwardRef<HTMLDivElement, LoadingStateProps>(
  ({ 
    className, 
    message = 'Loading...', 
    size = 'md', 
    variant = 'default',
    fullScreen = false,
    compact = false,
    showSpinner = true,
    ...props 
  }, ref) => {
    const containerClasses = fullScreen 
      ? 'fixed inset-0 bg-white bg-opacity-75 z-50 flex items-center justify-center safe-area-inset'
      : compact 
        ? 'flex items-center justify-center py-4'
        : 'flex items-center justify-center py-6 sm:py-8'

    return (
      <div
        ref={ref}
        className={cn(containerClasses, className)}
        {...props}
      >
        <div className={cn(
          'text-center',
          compact ? 'space-y-2' : 'space-y-3 sm:space-y-4'
        )}>
          {showSpinner && (
            <Spinner 
              size={size} 
              variant={variant} 
              className={compact ? 'mb-2' : 'mb-3 sm:mb-4'} 
            />
          )}
          <p className={cn(
            'text-gray-600 px-4',
            size === 'sm' && 'text-xs sm:text-sm',
            size === 'md' && 'text-sm sm:text-base',
            size === 'lg' && 'text-base sm:text-lg',
            size === 'xl' && 'text-lg sm:text-xl',
            compact && 'text-xs sm:text-sm'
          )}>
            {message}
          </p>
        </div>
      </div>
    )
  }
)
LoadingState.displayName = 'LoadingState'

export { LoadingState }