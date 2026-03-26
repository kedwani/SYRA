/**
 * Root Layout with Providers
 * Sets up QueryClient, Theme, and global accessibility features
 */

'use client';

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { reducedMotionCSS } from '@/lib/accessibility';

export interface RootLayoutProps {
  children: React.ReactNode;
}

// Create a client
const makeQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        refetchOnWindowFocus: false,
      },
    },
  });

let browserQueryClient: QueryClient | undefined = undefined;

function getQueryClient() {
  if (typeof window === 'undefined') {
    // Server: always make a new query client
    return makeQueryClient();
  } else {
    // Browser: make a new query client if we don't already have one
    if (!browserQueryClient) browserQueryClient = makeQueryClient();
    return browserQueryClient;
  }
}

export default function RootLayoutWithProviders({ children }: RootLayoutProps) {
  const queryClient = getQueryClient();

  return (
    <html lang="en" dir="ltr">
      <head>
        {/* CSS Variables for theming */}
        <style dangerouslySetInnerHTML={{ __html: reducedMotionCSS }} />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  );
}