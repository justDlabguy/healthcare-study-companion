"use client";

import { useRef, useCallback, useEffect } from "react";

interface TouchGestureOptions {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onTap?: () => void;
  onDoubleTap?: () => void;
  onLongPress?: () => void;
  swipeThreshold?: number;
  longPressDelay?: number;
  doubleTapDelay?: number;
}

interface TouchPoint {
  x: number;
  y: number;
  time: number;
}

export function useTouchGestures(options: TouchGestureOptions = {}) {
  const {
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    onTap,
    onDoubleTap,
    onLongPress,
    swipeThreshold = 50,
    longPressDelay = 500,
    doubleTapDelay = 300,
  } = options;

  const touchStart = useRef<TouchPoint | null>(null);
  const touchEnd = useRef<TouchPoint | null>(null);
  const lastTap = useRef<TouchPoint | null>(null);
  const longPressTimer = useRef<NodeJS.Timeout | null>(null);
  const isLongPress = useRef(false);

  const handleTouchStart = useCallback(
    (e: TouchEvent) => {
      const touch = e.touches[0];
      const now = Date.now();

      touchStart.current = {
        x: touch.clientX,
        y: touch.clientY,
        time: now,
      };

      touchEnd.current = null;
      isLongPress.current = false;

      // Start long press timer
      if (onLongPress) {
        longPressTimer.current = setTimeout(() => {
          isLongPress.current = true;
          onLongPress();
        }, longPressDelay);
      }
    },
    [onLongPress, longPressDelay]
  );

  const handleTouchMove = useCallback(() => {
    // Cancel long press if user moves finger
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }
  }, []);

  const handleTouchEnd = useCallback(
    (e: TouchEvent) => {
      if (!touchStart.current) return;

      const touch = e.changedTouches[0];
      const now = Date.now();

      touchEnd.current = {
        x: touch.clientX,
        y: touch.clientY,
        time: now,
      };

      // Clear long press timer
      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current);
        longPressTimer.current = null;
      }

      // Don't process other gestures if it was a long press
      if (isLongPress.current) {
        return;
      }

      const deltaX = touchEnd.current.x - touchStart.current.x;
      const deltaY = touchEnd.current.y - touchStart.current.y;
      const deltaTime = touchEnd.current.time - touchStart.current.time;

      const absX = Math.abs(deltaX);
      const absY = Math.abs(deltaY);

      // Check for swipe gestures
      if (absX > swipeThreshold || absY > swipeThreshold) {
        if (absX > absY) {
          // Horizontal swipe
          if (deltaX > 0 && onSwipeRight) {
            onSwipeRight();
          } else if (deltaX < 0 && onSwipeLeft) {
            onSwipeLeft();
          }
        } else {
          // Vertical swipe
          if (deltaY > 0 && onSwipeDown) {
            onSwipeDown();
          } else if (deltaY < 0 && onSwipeUp) {
            onSwipeUp();
          }
        }
        return;
      }

      // Check for tap gestures (small movement, quick time)
      if (absX < 10 && absY < 10 && deltaTime < 300) {
        // Check for double tap
        if (onDoubleTap && lastTap.current) {
          const timeSinceLastTap = now - lastTap.current.time;
          const distanceFromLastTap = Math.sqrt(
            Math.pow(touchEnd.current.x - lastTap.current.x, 2) +
              Math.pow(touchEnd.current.y - lastTap.current.y, 2)
          );

          if (timeSinceLastTap < doubleTapDelay && distanceFromLastTap < 50) {
            onDoubleTap();
            lastTap.current = null;
            return;
          }
        }

        // Single tap
        lastTap.current = touchEnd.current;

        // Delay single tap to allow for double tap detection
        if (onTap) {
          setTimeout(() => {
            if (lastTap.current === touchEnd.current) {
              onTap();
            }
          }, doubleTapDelay);
        }
      }
    },
    [
      onSwipeLeft,
      onSwipeRight,
      onSwipeUp,
      onSwipeDown,
      onTap,
      onDoubleTap,
      swipeThreshold,
      doubleTapDelay,
    ]
  );

  const attachGestures = useCallback(
    (element: HTMLElement | null) => {
      if (!element) return;

      element.addEventListener("touchstart", handleTouchStart, {
        passive: true,
      });
      element.addEventListener("touchmove", handleTouchMove, { passive: true });
      element.addEventListener("touchend", handleTouchEnd, { passive: true });

      return () => {
        element.removeEventListener("touchstart", handleTouchStart);
        element.removeEventListener("touchmove", handleTouchMove);
        element.removeEventListener("touchend", handleTouchEnd);

        if (longPressTimer.current) {
          clearTimeout(longPressTimer.current);
        }
      };
    },
    [handleTouchStart, handleTouchMove, handleTouchEnd]
  );

  return { attachGestures };
}

// Hook for pull-to-refresh functionality
interface PullToRefreshOptions {
  onRefresh: () => Promise<void>;
  threshold?: number;
  resistance?: number;
}

export function usePullToRefresh({
  onRefresh,
  threshold = 80,
  resistance = 2.5,
}: PullToRefreshOptions) {
  const isRefreshing = useRef(false);
  const startY = useRef(0);
  const currentY = useRef(0);
  const pullDistance = useRef(0);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (window.scrollY > 0) return;

    startY.current = e.touches[0].clientY;
  }, []);

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (window.scrollY > 0 || isRefreshing.current) return;

      currentY.current = e.touches[0].clientY;
      pullDistance.current = Math.max(
        0,
        (currentY.current - startY.current) / resistance
      );

      if (pullDistance.current > 0) {
        e.preventDefault();

        // Update UI to show pull distance
        const element = e.currentTarget as HTMLElement;
        if (element) {
          element.style.transform = `translateY(${pullDistance.current}px)`;
          element.style.transition = "none";
        }
      }
    },
    [resistance]
  );

  const handleTouchEnd = useCallback(async () => {
    if (isRefreshing.current) return;

    const element = document.documentElement;

    if (pullDistance.current > threshold) {
      isRefreshing.current = true;

      try {
        await onRefresh();
      } finally {
        isRefreshing.current = false;
      }
    }

    // Reset UI
    element.style.transform = "";
    element.style.transition = "transform 0.3s ease";

    setTimeout(() => {
      element.style.transition = "";
    }, 300);

    pullDistance.current = 0;
  }, [onRefresh, threshold]);

  const attachPullToRefresh = useCallback(
    (element: HTMLElement | null) => {
      if (!element) return;

      element.addEventListener("touchstart", handleTouchStart, {
        passive: true,
      });
      element.addEventListener("touchmove", handleTouchMove, {
        passive: false,
      });
      element.addEventListener("touchend", handleTouchEnd, { passive: true });

      return () => {
        element.removeEventListener("touchstart", handleTouchStart);
        element.removeEventListener("touchmove", handleTouchMove);
        element.removeEventListener("touchend", handleTouchEnd);
      };
    },
    [handleTouchStart, handleTouchMove, handleTouchEnd]
  );

  return { attachPullToRefresh, isRefreshing: isRefreshing.current };
}

// Hook for swipe-to-dismiss functionality
interface SwipeToDismissOptions {
  onDismiss: () => void;
  threshold?: number;
  direction?: "left" | "right" | "both";
}

export function useSwipeToDismiss({
  onDismiss,
  threshold = 100,
  direction = "both",
}: SwipeToDismissOptions) {
  const startX = useRef(0);
  const currentX = useRef(0);
  const isDismissing = useRef(false);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    startX.current = e.touches[0].clientX;
    isDismissing.current = false;
  }, []);

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (isDismissing.current) return;

      currentX.current = e.touches[0].clientX;
      const deltaX = currentX.current - startX.current;

      // Check direction constraints
      if (direction === "left" && deltaX > 0) return;
      if (direction === "right" && deltaX < 0) return;

      const element = e.currentTarget as HTMLElement;
      if (element && Math.abs(deltaX) > 10) {
        element.style.transform = `translateX(${deltaX}px)`;
        element.style.transition = "none";

        // Add visual feedback
        const opacity = Math.max(0.3, 1 - Math.abs(deltaX) / (threshold * 2));
        element.style.opacity = opacity.toString();
      }
    },
    [direction, threshold]
  );

  const handleTouchEnd = useCallback(() => {
    const deltaX = currentX.current - startX.current;
    const element = document.querySelector(
      "[data-swipe-target]"
    ) as HTMLElement;

    if (Math.abs(deltaX) > threshold) {
      isDismissing.current = true;

      if (element) {
        element.style.transform = `translateX(${
          deltaX > 0 ? "100%" : "-100%"
        })`;
        element.style.transition = "transform 0.3s ease, opacity 0.3s ease";
        element.style.opacity = "0";
      }

      setTimeout(() => {
        onDismiss();
      }, 300);
    } else {
      // Reset position
      if (element) {
        element.style.transform = "";
        element.style.opacity = "";
        element.style.transition = "transform 0.3s ease, opacity 0.3s ease";

        setTimeout(() => {
          element.style.transition = "";
        }, 300);
      }
    }
  }, [onDismiss, threshold]);

  const attachSwipeToDismiss = useCallback(
    (element: HTMLElement | null) => {
      if (!element) return;

      element.setAttribute("data-swipe-target", "true");
      element.addEventListener("touchstart", handleTouchStart, {
        passive: true,
      });
      element.addEventListener("touchmove", handleTouchMove, { passive: true });
      element.addEventListener("touchend", handleTouchEnd, { passive: true });

      return () => {
        element.removeAttribute("data-swipe-target");
        element.removeEventListener("touchstart", handleTouchStart);
        element.removeEventListener("touchmove", handleTouchMove);
        element.removeEventListener("touchend", handleTouchEnd);
      };
    },
    [handleTouchStart, handleTouchMove, handleTouchEnd]
  );

  return { attachSwipeToDismiss };
}

export default useTouchGestures;
