"use client";

import React, { useState, useEffect, useRef } from "react";
import { X, ChevronLeft, ChevronRight, Check, Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface TourStep {
  id: string;
  title: string;
  content: string;
  target: string; // CSS selector
  position?: "top" | "bottom" | "left" | "right" | "center";
  action?: {
    label: string;
    onClick: () => void;
  };
  optional?: boolean;
}

interface OnboardingTourProps {
  steps: TourStep[];
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  tourId: string;
}

export function OnboardingTour({
  steps,
  isOpen,
  onClose,
  onComplete,
  tourId,
}: OnboardingTourProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Update target element and position when step changes
  useEffect(() => {
    if (!isOpen || !steps[currentStep]) return;

    const step = steps[currentStep];
    const element = document.querySelector(step.target) as HTMLElement;

    if (element) {
      setTargetElement(element);

      // Scroll element into view
      element.scrollIntoView({
        behavior: "smooth",
        block: "center",
        inline: "center",
      });

      // Add highlight
      element.style.position = "relative";
      element.style.zIndex = "1001";
      element.style.boxShadow =
        "0 0 0 4px rgba(59, 130, 246, 0.5), 0 0 0 9999px rgba(0, 0, 0, 0.5)";
      element.style.borderRadius = "8px";

      // Calculate tooltip position
      setTimeout(() => {
        updateTooltipPosition(element, step.position || "bottom");
      }, 100);
    }

    return () => {
      if (element) {
        element.style.position = "";
        element.style.zIndex = "";
        element.style.boxShadow = "";
        element.style.borderRadius = "";
      }
    };
  }, [currentStep, isOpen, steps]);

  const updateTooltipPosition = (element: HTMLElement, position: string) => {
    if (!tooltipRef.current) return;

    const elementRect = element.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let x = 0;
    let y = 0;

    switch (position) {
      case "top":
        x = elementRect.left + elementRect.width / 2 - tooltipRect.width / 2;
        y = elementRect.top - tooltipRect.height - 12;
        break;
      case "bottom":
        x = elementRect.left + elementRect.width / 2 - tooltipRect.width / 2;
        y = elementRect.bottom + 12;
        break;
      case "left":
        x = elementRect.left - tooltipRect.width - 12;
        y = elementRect.top + elementRect.height / 2 - tooltipRect.height / 2;
        break;
      case "right":
        x = elementRect.right + 12;
        y = elementRect.top + elementRect.height / 2 - tooltipRect.height / 2;
        break;
      case "center":
        x = viewportWidth / 2 - tooltipRect.width / 2;
        y = viewportHeight / 2 - tooltipRect.height / 2;
        break;
    }

    // Keep tooltip within viewport
    x = Math.max(12, Math.min(x, viewportWidth - tooltipRect.width - 12));
    y = Math.max(12, Math.min(y, viewportHeight - tooltipRect.height - 12));

    setTooltipPosition({ x, y });
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // Mark tour as completed in localStorage
    localStorage.setItem(`tour-completed-${tourId}`, "true");
    onComplete();
    onClose();
  };

  const handleSkip = () => {
    localStorage.setItem(`tour-skipped-${tourId}`, "true");
    onClose();
  };

  if (!isOpen || !steps[currentStep]) return null;

  const step = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-1000 bg-black/50 backdrop-blur-sm" />

      {/* Tooltip */}
      <div
        ref={tooltipRef}
        className="fixed z-1002 w-80 max-w-[calc(100vw-2rem)] bg-white rounded-xl shadow-xl border border-slate-200"
        style={{
          left: tooltipPosition.x,
          top: tooltipPosition.y,
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 bg-blue-100 rounded-lg">
              <Lightbulb className="h-4 w-4 text-blue-600" />
            </div>
            <h3 className="font-semibold text-slate-900">{step.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          <p className="text-sm text-slate-600 leading-relaxed mb-4">
            {step.content}
          </p>

          {/* Action Button */}
          {step.action && (
            <div className="mb-4">
              <Button
                onClick={step.action.onClick}
                variant="outline"
                size="sm"
                className="w-full"
              >
                {step.action.label}
              </Button>
            </div>
          )}

          {/* Progress */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex space-x-1">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={cn(
                    "w-2 h-2 rounded-full transition-colors",
                    index === currentStep
                      ? "bg-blue-600"
                      : index < currentStep
                      ? "bg-blue-300"
                      : "bg-slate-200"
                  )}
                />
              ))}
            </div>
            <span className="text-xs text-slate-500">
              {currentStep + 1} of {steps.length}
            </span>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <div className="flex space-x-2">
              {!isFirstStep && (
                <Button
                  onClick={handlePrevious}
                  variant="outline"
                  size="sm"
                  className="flex items-center space-x-1"
                >
                  <ChevronLeft className="h-4 w-4" />
                  <span>Previous</span>
                </Button>
              )}
            </div>

            <div className="flex space-x-2">
              {step.optional && (
                <Button
                  onClick={handleSkip}
                  variant="ghost"
                  size="sm"
                  className="text-slate-500"
                >
                  Skip
                </Button>
              )}

              <Button
                onClick={handleNext}
                size="sm"
                className="flex items-center space-x-1"
              >
                {isLastStep ? (
                  <>
                    <Check className="h-4 w-4" />
                    <span>Complete</span>
                  </>
                ) : (
                  <>
                    <span>Next</span>
                    <ChevronRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// Hook to manage onboarding tours
export function useOnboardingTour(tourId: string) {
  const [isOpen, setIsOpen] = useState(false);

  const startTour = () => {
    setIsOpen(true);
  };

  const closeTour = () => {
    setIsOpen(false);
  };

  const isCompleted = () => {
    return localStorage.getItem(`tour-completed-${tourId}`) === "true";
  };

  const isSkipped = () => {
    return localStorage.getItem(`tour-skipped-${tourId}`) === "true";
  };

  const shouldShowTour = () => {
    return !isCompleted() && !isSkipped();
  };

  const resetTour = () => {
    localStorage.removeItem(`tour-completed-${tourId}`);
    localStorage.removeItem(`tour-skipped-${tourId}`);
  };

  return {
    isOpen,
    startTour,
    closeTour,
    isCompleted,
    isSkipped,
    shouldShowTour,
    resetTour,
  };
}

export default OnboardingTour;
