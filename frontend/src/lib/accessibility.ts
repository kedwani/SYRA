/**
 * Accessibility Utilities
 * Provides hooks and utilities for accessibility features
 * including reduced motion detection, focus management, and screen reader support
 */

import { useState, useEffect, useCallback } from 'react';

/**
 * Hook to detect if user prefers reduced motion
 * Implements WCAG 2.3.3: Animation from Interactions
 * @returns boolean indicating if reduced motion is preferred
 */
export const usePrefersReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    // Check for match media support
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    if (mediaQuery.matches) {
      setPrefersReducedMotion(true);
    }

    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return prefersReducedMotion;
};

/**
 * Hook to manage focus trapping within a container
 * Useful for modals and dialogs
 */
export const useFocusTrap = (isActive: boolean = true) => {
  const [focusableElements, setFocusableElements] = useState<HTMLElement[]>([]);
  const [focusedIndex, setFocusedIndex] = useState(0);

  useEffect(() => {
    if (!isActive) return;

    const updateFocusableElements = () => {
      const elements = Array.from(
        document.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
      ).filter((el) => !el.hasAttribute('disabled') && el.offsetParent !== null);

      setFocusableElements(elements);
    };

    updateFocusableElements();

    const interval = setInterval(updateFocusableElements, 100);
    return () => clearInterval(interval);
  }, [isActive]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (focusableElements.length === 0) return;

      if (event.key === 'Tab') {
        event.preventDefault();
        
        const nextIndex = event.shiftKey
          ? (focusedIndex - 1 + focusableElements.length) % focusableElements.length
          : (focusedIndex + 1) % focusableElements.length;

        setFocusedIndex(nextIndex);
        focusableElements[nextIndex]?.focus();
      }
    },
    [focusableElements, focusedIndex]
  );

  return { handleKeyDown };
};

/**
 * Hook for announcements to screen readers
 * Uses aria-live regions for dynamic content updates
 */
export const useAnnounce = () => {
  const [announcement, setAnnouncement] = useState('');
  const [priority, setPriority] = useState<'polite' | 'assertive'>('polite');

  const announce = useCallback((message: string, urgency: 'polite' | 'assertive' = 'polite') => {
    setPriority(urgency);
    setAnnouncement('');
    
    // Small delay to ensure screen reader picks up the change
    setTimeout(() => {
      setAnnouncement(message);
    }, 100);
  }, []);

  return { announcement, priority, announce };
};

/**
 * LiveRegion component for screen reader announcements
 */
interface LiveRegionProps {
  message: string;
  priority?: 'polite' | 'assertive';
}

export const LiveRegion = ({ message, priority = 'polite' }: LiveRegionProps) => {
  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
};

/**
 * Generate unique ID for accessibility attributes
 */
export const useId = (prefix: string = 'syra'): string => {
  const [id, setId] = useState('');

  useEffect(() => {
    setId(`${prefix}-${Math.random().toString(36).substring(2, 9)}`);
  }, [prefix]);

  return id;
};

/**
 * Check if element is visible in viewport
 */
export const useInViewport = (ref: React.RefObject<HTMLElement>): boolean => {
  const [isInViewport, setIsInViewport] = useState(false);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsInViewport(entry.isIntersecting);
      },
      { threshold: 0 }
    );

    observer.observe(ref.current);

    return () => {
      observer.disconnect();
    };
  }, [ref]);

  return isInViewport;
};

/**
 * CSS for reduced motion support
 * Add this to your global CSS or use with styled-components
 */
export const reducedMotionCSS = `
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
`;