/**
 * Performance utilities for optimizing the app on slower connections
 */

// Connection quality detection
export function getConnectionQuality(): 'slow' | 'fast' | 'unknown' {
  if (typeof navigator === 'undefined' || !('connection' in navigator)) {
    return 'unknown';
  }

  const connection = (navigator as any).connection;
  
  if (!connection) return 'unknown';

  // Check effective connection type
  const effectiveType = connection.effectiveType;
  
  if (effectiveType === 'slow-2g' || effectiveType === '2g') {
    return 'slow';
  }
  
  if (effectiveType === '3g' && connection.downlink < 1.5) {
    return 'slow';
  }
  
  return 'fast';
}

// Debounce utility for search inputs
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Throttle utility for scroll events
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Lazy loading utility
export function createIntersectionObserver(
  callback: (entries: IntersectionObserverEntry[]) => void,
  options?: IntersectionObserverInit
): IntersectionObserver | null {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
    return null;
  }

  return new IntersectionObserver(callback, {
    rootMargin: '50px',
    threshold: 0.1,
    ...options,
  });
}

// Image optimization
export function getOptimizedImageSrc(
  src: string,
  width: number,
  quality: number = 75
): string {
  // For Next.js Image optimization
  if (src.startsWith('/')) {
    return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality}`;
  }
  
  return src;
}

// Bundle size optimization - dynamic imports
export function loadComponentLazily<T>(
  importFn: () => Promise<{ default: T }>
): Promise<T> {
  return importFn().then(module => module.default);
}

// Memory management
export function cleanupEventListeners(
  element: Element | Window,
  events: Array<{ type: string; listener: EventListener; options?: boolean | AddEventListenerOptions }>
): void {
  events.forEach(({ type, listener, options }) => {
    element.removeEventListener(type, listener, options);
  });
}

// Preload critical resources
export function preloadResource(href: string, as: string, type?: string): void {
  if (typeof document === 'undefined') return;

  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = href;
  link.as = as;
  if (type) link.type = type;
  
  document.head.appendChild(link);
}

// Check if user prefers reduced motion
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Adaptive loading based on connection
export function shouldLoadHeavyContent(): boolean {
  const connectionQuality = getConnectionQuality();
  
  // Don't load heavy content on slow connections
  if (connectionQuality === 'slow') return false;
  
  // Check if user is on a mobile device with limited data
  if (typeof navigator !== 'undefined' && 'connection' in navigator) {
    const connection = (navigator as any).connection;
    if (connection?.saveData) return false;
  }
  
  return true;
}

// Performance monitoring
export function measurePerformance(name: string, fn: () => void): void {
  if (typeof performance === 'undefined') {
    fn();
    return;
  }

  const start = performance.now();
  fn();
  const end = performance.now();
  
  console.log(`${name} took ${end - start} milliseconds`);
}

// Async performance measurement
export async function measureAsyncPerformance<T>(
  name: string,
  fn: () => Promise<T>
): Promise<T> {
  if (typeof performance === 'undefined') {
    return fn();
  }

  const start = performance.now();
  const result = await fn();
  const end = performance.now();
  
  console.log(`${name} took ${end - start} milliseconds`);
  return result;
}