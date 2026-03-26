/**
 * SkipLink Component
 * Accessibility component - "Skip to main content" link
 * WCAG 2.4.1: Bypass Blocks - Allows keyboard users to skip navigation
 * Hidden by default, visible on focus
 */

import React, { AnchorHTMLAttributes } from 'react';

export interface SkipLinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  targetId?: string;
}

export const SkipLink = ({
  targetId = 'main-content',
  className = '',
  children = 'Skip to main content',
  ...props
}: SkipLinkProps) => {
  const baseStyles = `
    absolute top-0 left-0 z-50
    -translate-y-full translate-x-4
    px-4 py-3 bg-blue-600 text-white font-semibold
    rounded-b-lg
    transition-transform duration-200
    focus:translate-y-0 focus:outline-none focus:ring-2 focus:ring-blue-500
    hover:bg-blue-700
  `;

  return (
    <a
      href={`#${targetId}`}
      className={`${baseStyles} ${className}`}
      {...props}
    >
      {children}
    </a>
  );
};

// SkipLink target marker component
export interface SkipLinkTargetProps {
  id?: string;
}

export const SkipLinkTarget = ({ id = 'main-content' }: SkipLinkTargetProps) => {
  return (
    <div
      id={id}
      tabIndex={-1}
      className="outline-none"
      aria-hidden="true"
    />
  );
};

export default SkipLink;