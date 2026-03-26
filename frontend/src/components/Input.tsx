/**
 * Input Component
 * Accessible form input with label, error handling, and helper text
 * Supports all standard input types with proper ARIA attributes
 */

import React, { InputHTMLAttributes, forwardRef, useId } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  hideLabel?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      hideLabel = false,
      id,
      className = '',
      required,
      disabled,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const inputId = id || generatedId;
    const errorId = `${inputId}-error`;
    const helperId = `${inputId}-helper`;

    const baseStyles = `
      block w-full rounded-lg border px-4 py-3
      transition-colors duration-200
      focus:outline-none focus:ring-2 focus:ring-offset-0
      disabled:bg-gray-100 disabled:cursor-not-allowed
    `;

    const stateStyles = error
      ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500';

    const iconWrapperStyles = leftIcon
      ? 'relative'
      : '';

    const iconStyles = leftIcon
      ? 'absolute inset-y-0 start-0 flex items-center ps-4 pointer-events-none'
      : '';
    
    const inputPadding = leftIcon ? 'ps-12' : 'ps-4';

    return (
      <div className={iconWrapperStyles}>
        {label && (
          <label
            htmlFor={inputId}
            className={`
              block text-sm font-semibold text-gray-700 mb-2
              ${hideLabel ? 'sr-only' : ''}
            `}
          >
            {label}
            {required && (
              <span className="text-red-500 ms-1" aria-hidden="true">
                *
              </span>
            )}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className={iconStyles}>
              <span className="text-gray-400">{leftIcon}</span>
            </div>
          )}
          
          <input
            ref={ref}
            id={inputId}
            required={required}
            disabled={disabled}
            aria-invalid={error ? 'true' : undefined}
            aria-describedby={
              error
                ? errorId
                : helperText
                ? helperId
                : undefined
            }
            className={`
              ${baseStyles}
              ${stateStyles}
              ${inputPadding}
              ${rightIcon ? 'pe-12' : 'pe-4'}
              bg-white text-gray-900 placeholder-gray-400
              ${className}
            `}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute inset-y-0 end-0 flex items-center pe-4 pointer-events-none">
              <span className="text-gray-400">{rightIcon}</span>
            </div>
          )}
        </div>

        {error && (
          <p
            id={errorId}
            className="mt-1.5 text-sm text-red-600"
            role="alert"
          >
            {error}
          </p>
        )}

        {helperText && !error && (
          <p
            id={helperId}
            className="mt-1.5 text-sm text-gray-500"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;