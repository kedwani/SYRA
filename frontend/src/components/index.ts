/**
 * SYRA Frontend Component Library
 * Accessible, reusable React components for the SYRA Medical ID platform
 * 
 * @package @syra/frontend
 * @version 1.0.0
 */

// Components
export { Button, type ButtonProps, type ButtonVariant, type ButtonSize } from './Button';
export { Input, type InputProps } from './Input';
export { Card, CardHeader, CardBody, CardFooter, type CardProps, type CardHeaderProps, type CardBodyProps, type CardFooterProps } from './Card';
export { SkipLink, SkipLinkTarget, type SkipLinkProps } from './SkipLink';

// Accessibility utilities (from lib)
export { 
  usePrefersReducedMotion, 
  useFocusTrap, 
  useAnnounce, 
  LiveRegion, 
  useId, 
  useInViewport,
  reducedMotionCSS 
} from '../lib/accessibility';

// State Management (from lib)
export { useUIStore, usePreferencesStore, useTheme, type UIState, type UserPreferences, type Toast } from '../lib/store';

// API utilities (from lib)
export { 
  api, 
  apiClient, 
  useApiQuery, 
  useApiMutation, 
  queryKeys,
  formatApiError,
  isNetworkError,
  type ApiResponse,
  type PaginatedResponse,
  type ApiError
} from '../lib/api';