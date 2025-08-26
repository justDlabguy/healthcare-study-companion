import { useState, useEffect } from 'react';

// Breakpoint values matching Tailwind config
const breakpoints = {
  xs: 475,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

type Breakpoint = keyof typeof breakpoints;

export function useResponsive() {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isAbove = (breakpoint: Breakpoint): boolean => {
    return windowSize.width >= breakpoints[breakpoint];
  };

  const isBelow = (breakpoint: Breakpoint): boolean => {
    return windowSize.width < breakpoints[breakpoint];
  };

  const isBetween = (min: Breakpoint, max: Breakpoint): boolean => {
    return windowSize.width >= breakpoints[min] && windowSize.width < breakpoints[max];
  };

  return {
    windowSize,
    isAbove,
    isBelow,
    isBetween,
    // Convenience properties
    isMobile: isBelow('sm'),
    isTablet: isBetween('sm', 'lg'),
    isDesktop: isAbove('lg'),
    isSmallScreen: isBelow('md'),
    isLargeScreen: isAbove('xl'),
  };
}

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const media = window.matchMedia(query);
    setMatches(media.matches);

    const listener = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}

// Hook for touch device detection
export function useTouchDevice(): boolean {
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const checkTouch = () => {
      setIsTouch(
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        (navigator as any).msMaxTouchPoints > 0
      );
    };

    checkTouch();
    
    // Listen for touch events to detect touch capability
    const handleTouchStart = () => setIsTouch(true);
    window.addEventListener('touchstart', handleTouchStart, { once: true });

    return () => {
      window.removeEventListener('touchstart', handleTouchStart);
    };
  }, []);

  return isTouch;
}

// Hook for reduced motion preference
export function useReducedMotion(): boolean {
  return useMediaQuery('(prefers-reduced-motion: reduce)');
}

// Hook for dark mode preference
export function useDarkMode(): boolean {
  return useMediaQuery('(prefers-color-scheme: dark)');
}

// Hook for high contrast preference
export function useHighContrast(): boolean {
  return useMediaQuery('(prefers-contrast: high)');
}

// Hook for connection quality
export function useConnectionQuality(): 'slow' | 'fast' | 'unknown' {
  const [quality, setQuality] = useState<'slow' | 'fast' | 'unknown'>('unknown');

  useEffect(() => {
    if (typeof navigator === 'undefined' || !('connection' in navigator)) {
      return;
    }

    const connection = (navigator as any).connection;
    if (!connection) return;

    const updateQuality = () => {
      const effectiveType = connection.effectiveType;
      
      if (effectiveType === 'slow-2g' || effectiveType === '2g') {
        setQuality('slow');
      } else if (effectiveType === '3g' && connection.downlink < 1.5) {
        setQuality('slow');
      } else {
        setQuality('fast');
      }
    };

    updateQuality();
    connection.addEventListener('change', updateQuality);

    return () => {
      connection.removeEventListener('change', updateQuality);
    };
  }, []);

  return quality;
}

// Hook for safe area insets (for mobile devices with notches)
export function useSafeAreaInsets() {
  const [insets, setInsets] = useState({
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const updateInsets = () => {
      const style = getComputedStyle(document.documentElement);
      
      setInsets({
        top: parseInt(style.getPropertyValue('env(safe-area-inset-top)') || '0'),
        right: parseInt(style.getPropertyValue('env(safe-area-inset-right)') || '0'),
        bottom: parseInt(style.getPropertyValue('env(safe-area-inset-bottom)') || '0'),
        left: parseInt(style.getPropertyValue('env(safe-area-inset-left)') || '0'),
      });
    };

    updateInsets();
    window.addEventListener('resize', updateInsets);
    window.addEventListener('orientationchange', updateInsets);

    return () => {
      window.removeEventListener('resize', updateInsets);
      window.removeEventListener('orientationchange', updateInsets);
    };
  }, []);

  return insets;
}