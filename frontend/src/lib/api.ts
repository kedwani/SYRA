/**
 * API Utilities
 * Type-safe API client with error handling, retry logic, and TypeScript support
 * Designed to work with Django REST Framework backend
 */

import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';

// ============================================
// Types
// ============================================

// Base API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

// Paginated response
export interface PaginatedResponse<T> {
  data: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

// Error response from API
export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  code?: string;
}

// Request options
export interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
}

// ============================================
// API Client
// ============================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';
const DEFAULT_TIMEOUT = 30000; // 30 seconds

/**
 * Get CSRF token from cookie
 */
const getCsrfToken = (): string => {
  if (typeof document === 'undefined') return '';
  
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return decodeURIComponent(value);
    }
  }
  return '';
};

/**
 * Main fetch wrapper with error handling
 */
export const apiClient = async <T>(
  endpoint: string,
  options: RequestOptions & {
    method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    body?: unknown;
  } = {}
): Promise<T> => {
  const {
    method = 'GET',
    body,
    headers = {},
    timeout = DEFAULT_TIMEOUT,
  } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    if (!contentType?.includes('application/json')) {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text() as unknown as T;
    }

    const data = await response.json();

    if (!response.ok) {
      const error: ApiError = {
        message: data.message || data.detail || 'An error occurred',
        errors: data.errors,
        code: data.code,
      };
      throw error;
    }

    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timed out');
      }
      throw error;
    }
    throw error;
  }
};

// ============================================
// Convenience Methods
// ============================================

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    apiClient<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body: unknown, options?: RequestOptions) =>
    apiClient<T>(endpoint, { ...options, method: 'POST', body }),

  put: <T>(endpoint: string, body: unknown, options?: RequestOptions) =>
    apiClient<T>(endpoint, { ...options, method: 'PUT', body }),

  patch: <T>(endpoint: string, body: unknown, options?: RequestOptions) =>
    apiClient<T>(endpoint, { ...options, method: 'PATCH', body }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    apiClient<T>(endpoint, { ...options, method: 'DELETE' }),
};

// ============================================
// React Query Hooks
// ============================================

/**
 * Type-safe useQuery wrapper with common defaults
 */
export const useApiQuery = <TData, TError = ApiError>(
  key: string[],
  endpoint: string,
  options?: Omit<UseQueryOptions<TData, TError>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<TData, TError>({
    queryKey: key,
    queryFn: () => api.get<TData>(endpoint),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
    ...options,
  });
};

/**
 * Type-safe useMutation wrapper with common defaults
 */
export const useApiMutation = <
  TVariables = unknown,
  TData = unknown,
  TError = ApiError
>(
  endpoint: string,
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST',
  options?: Omit<UseMutationOptions<TData, TError, TVariables>, 'mutationFn'>
) => {
  return useMutation<TData, TError, TVariables>({
    mutationFn: (variables) => {
      const methods: Record<string, (url: string, body: unknown) => Promise<TData>> = {
        POST: (url, body) => api.post<TData>(url, body),
        PUT: (url, body) => api.put<TData>(url, body),
        PATCH: (url, body) => api.patch<TData>(url, body),
        DELETE: (url) => api.delete<TData>(url),
      };
      return methods[method](endpoint, variables);
    },
    retry: 1,
    ...options,
  });
};

// ============================================
// Error Handling
// ============================================

/**
 * Format API error for display
 */
export const formatApiError = (error: unknown): string => {
  if (typeof error === 'string') return error;
  
  if (error && typeof error === 'object' && 'message' in error) {
    return (error as ApiError).message;
  }
  
  return 'An unexpected error occurred. Please try again.';
};

/**
 * Check if error is a network error
 */
export const isNetworkError = (error: unknown): boolean => {
  return (
    error instanceof TypeError &&
    error.message === 'Failed to fetch'
  );
};

// ============================================
// Query Key Factory
// ============================================

export const queryKeys = {
  // User queries
  user: ['user'] as const,
  profile: ['profile'] as const,
  medicalProfile: (id: string) => ['medicalProfile', id] as const,
  
  // Store queries
  products: ['products'] as const,
  product: (id: string) => ['product', id] as const,
  cart: ['cart'] as const,
  orders: ['orders'] as const,
  order: (id: string) => ['order', id] as const,
  
  // Common
  users: ['users'] as const,
  doctors: ['doctors'] as const,
};