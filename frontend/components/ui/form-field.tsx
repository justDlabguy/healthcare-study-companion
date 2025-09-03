"use client";

import React, { useState, useEffect } from "react";
import { Check, AlertCircle, Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface FormFieldProps {
  label: string;
  type?: "text" | "email" | "password" | "textarea" | "number";
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  error?: string;
  success?: string;
  required?: boolean;
  disabled?: boolean;
  autoComplete?: string;
  maxLength?: number;
  minLength?: number;
  pattern?: string;
  rows?: number;
  className?: string;
  hint?: string;
  showCharCount?: boolean;
  validateOnChange?: boolean;
  customValidation?: (value: string) => string | null;
}

export function FormField({
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  onBlur,
  error,
  success,
  required = false,
  disabled = false,
  autoComplete,
  maxLength,
  minLength,
  pattern,
  rows = 3,
  className,
  hint,
  showCharCount = false,
  validateOnChange = false,
  customValidation,
}: FormFieldProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [internalError, setInternalError] = useState<string | null>(null);
  const [hasBeenBlurred, setHasBeenBlurred] = useState(false);

  // Real-time validation
  useEffect(() => {
    if (validateOnChange && hasBeenBlurred && value) {
      validateField(value);
    }
  }, [value, validateOnChange, hasBeenBlurred]);

  const validateField = (fieldValue: string) => {
    let validationError: string | null = null;

    // Required validation
    if (required && !fieldValue.trim()) {
      validationError = `${label} is required`;
    }
    // Length validation
    else if (minLength && fieldValue.length < minLength) {
      validationError = `${label} must be at least ${minLength} characters`;
    } else if (maxLength && fieldValue.length > maxLength) {
      validationError = `${label} must be no more than ${maxLength} characters`;
    }
    // Email validation
    else if (type === "email" && fieldValue) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(fieldValue)) {
        validationError = "Please enter a valid email address";
      }
    }
    // Pattern validation
    else if (pattern && fieldValue) {
      const regex = new RegExp(pattern);
      if (!regex.test(fieldValue)) {
        validationError = `${label} format is invalid`;
      }
    }
    // Custom validation
    else if (customValidation && fieldValue) {
      validationError = customValidation(fieldValue);
    }

    setInternalError(validationError);
    return validationError;
  };

  const handleBlur = () => {
    setIsFocused(false);
    setHasBeenBlurred(true);
    if (validateOnChange) {
      validateField(value);
    }
    onBlur?.();
  };

  const handleFocus = () => {
    setIsFocused(true);
  };

  const displayError = error || internalError;
  const isValid = !displayError && value && hasBeenBlurred;
  const showSuccess = success || (isValid && validateOnChange);

  const inputClasses = cn(
    "w-full px-4 py-3 border rounded-lg transition-all duration-200 bg-white",
    "focus:outline-none focus:ring-2 focus:ring-offset-1",
    {
      // Default state
      "border-slate-200 focus:border-blue-500 focus:ring-blue-500/20":
        !displayError && !showSuccess,
      // Error state
      "border-red-300 focus:border-red-500 focus:ring-red-500/20 bg-red-50/50":
        displayError,
      // Success state
      "border-green-300 focus:border-green-500 focus:ring-green-500/20 bg-green-50/50":
        showSuccess,
      // Disabled state
      "bg-slate-50 text-slate-500 cursor-not-allowed": disabled,
      // Focused state
      "ring-2": isFocused,
    },
    className
  );

  const labelClasses = cn(
    "block text-sm font-medium mb-2 transition-colors duration-200",
    {
      "text-slate-700": !displayError && !showSuccess,
      "text-red-700": displayError,
      "text-green-700": showSuccess,
      "text-slate-500": disabled,
    }
  );

  const renderInput = () => {
    const commonProps = {
      value,
      onChange: (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
      ) => onChange(e.target.value),
      onFocus: handleFocus,
      onBlur: handleBlur,
      placeholder,
      disabled,
      autoComplete,
      maxLength,
      className: inputClasses,
      "aria-invalid": !!displayError,
      "aria-describedby": displayError ? `${label}-error` : undefined,
    };

    if (type === "textarea") {
      return <textarea {...commonProps} rows={rows} />;
    }

    if (type === "password") {
      return (
        <div className="relative">
          <input
            {...commonProps}
            type={showPassword ? "text" : "password"}
            className={cn(inputClasses, "pr-12")}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
            tabIndex={-1}
          >
            {showPassword ? (
              <EyeOff className="h-5 w-5" />
            ) : (
              <Eye className="h-5 w-5" />
            )}
          </button>
        </div>
      );
    }

    return <input {...commonProps} type={type} />;
  };

  return (
    <div className="space-y-2">
      <label className={labelClasses}>
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative">
        {renderInput()}

        {/* Success icon */}
        {showSuccess && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Check className="h-5 w-5 text-green-500" />
          </div>
        )}

        {/* Error icon */}
        {displayError && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <AlertCircle className="h-5 w-5 text-red-500" />
          </div>
        )}
      </div>

      {/* Character count */}
      {showCharCount && maxLength && (
        <div className="text-right">
          <span
            className={cn(
              "text-xs",
              value.length > maxLength * 0.9 ? "text-red-500" : "text-slate-500"
            )}
          >
            {value.length}/{maxLength}
          </span>
        </div>
      )}

      {/* Error message */}
      {displayError && (
        <div
          id={`${label}-error`}
          className="flex items-center gap-1 text-red-600 text-sm animate-slide-up"
        >
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{displayError}</span>
        </div>
      )}

      {/* Success message */}
      {success && (
        <div className="flex items-center gap-1 text-green-600 text-sm animate-slide-up">
          <Check className="h-4 w-4 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {/* Hint */}
      {hint && !displayError && !success && (
        <div className="text-slate-500 text-sm">{hint}</div>
      )}
    </div>
  );
}

export default FormField;
