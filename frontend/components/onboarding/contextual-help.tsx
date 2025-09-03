"use client";

import React, { useState, useRef, useEffect } from "react";
import { HelpCircle, X, ExternalLink, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface HelpTooltipProps {
  content: string;
  title?: string;
  position?: "top" | "bottom" | "left" | "right";
  size?: "sm" | "md" | "lg";
  trigger?: "hover" | "click";
  className?: string;
  children?: React.ReactNode;
  learnMoreUrl?: string;
}

export function HelpTooltip({
  content,
  title,
  position = "top",
  size = "md",
  trigger = "hover",
  className,
  children,
  learnMoreUrl,
}: HelpTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const sizeClasses = {
    sm: "w-48 text-xs",
    md: "w-64 text-sm",
    lg: "w-80 text-sm",
  };

  const updatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let x = 0;
    let y = 0;

    switch (position) {
      case "top":
        x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        y = triggerRect.top - tooltipRect.height - 8;
        break;
      case "bottom":
        x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        y = triggerRect.bottom + 8;
        break;
      case "left":
        x = triggerRect.left - tooltipRect.width - 8;
        y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        break;
      case "right":
        x = triggerRect.right + 8;
        y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        break;
    }

    // Keep tooltip within viewport
    x = Math.max(8, Math.min(x, viewportWidth - tooltipRect.width - 8));
    y = Math.max(8, Math.min(y, viewportHeight - tooltipRect.height - 8));

    setTooltipPosition({ x, y });
  };

  const showTooltip = () => {
    setIsVisible(true);
    setTimeout(updatePosition, 0);
  };

  const hideTooltip = () => {
    setIsVisible(false);
  };

  const handleMouseEnter = () => {
    if (trigger === "hover") {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      showTooltip();
    }
  };

  const handleMouseLeave = () => {
    if (trigger === "hover") {
      timeoutRef.current = setTimeout(hideTooltip, 100);
    }
  };

  const handleClick = () => {
    if (trigger === "click") {
      if (isVisible) {
        hideTooltip();
      } else {
        showTooltip();
      }
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        trigger === "click" &&
        isVisible &&
        tooltipRef.current &&
        !tooltipRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        hideTooltip();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [trigger, isVisible]);

  useEffect(() => {
    if (isVisible) {
      updatePosition();
    }
  }, [isVisible, position]);

  return (
    <>
      <div
        ref={triggerRef}
        className={cn("inline-flex items-center", className)}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
      >
        {children || (
          <button className="p-1 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-colors">
            <HelpCircle className="h-4 w-4" />
          </button>
        )}
      </div>

      {isVisible && (
        <>
          {/* Backdrop for click trigger */}
          {trigger === "click" && (
            <div className="fixed inset-0 z-40" onClick={hideTooltip} />
          )}

          {/* Tooltip */}
          <div
            ref={tooltipRef}
            className={cn(
              "fixed z-50 bg-white rounded-lg shadow-lg border border-slate-200 p-3",
              sizeClasses[size]
            )}
            style={{
              left: tooltipPosition.x,
              top: tooltipPosition.y,
            }}
            onMouseEnter={() => {
              if (trigger === "hover" && timeoutRef.current) {
                clearTimeout(timeoutRef.current);
              }
            }}
            onMouseLeave={handleMouseLeave}
          >
            {/* Header */}
            {title && (
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-slate-900">{title}</h4>
                {trigger === "click" && (
                  <button
                    onClick={hideTooltip}
                    className="p-1 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </div>
            )}

            {/* Content */}
            <p className="text-slate-600 leading-relaxed">{content}</p>

            {/* Learn More Link */}
            {learnMoreUrl && (
              <div className="mt-3 pt-2 border-t border-slate-100">
                <a
                  href={learnMoreUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-700 text-xs font-medium"
                >
                  <span>Learn more</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            )}

            {/* Arrow */}
            <div
              className={cn(
                "absolute w-2 h-2 bg-white border-slate-200 transform rotate-45",
                {
                  "bottom-full left-1/2 -translate-x-1/2 border-b border-r":
                    position === "top",
                  "top-full left-1/2 -translate-x-1/2 border-t border-l":
                    position === "bottom",
                  "right-full top-1/2 -translate-y-1/2 border-t border-r":
                    position === "left",
                  "left-full top-1/2 -translate-y-1/2 border-b border-l":
                    position === "right",
                }
              )}
            />
          </div>
        </>
      )}
    </>
  );
}

// Contextual help for specific features
interface FeatureHelpProps {
  feature: string;
  className?: string;
}

export function FeatureHelp({ feature, className }: FeatureHelpProps) {
  const helpContent = {
    "topic-creation": {
      title: "Creating Topics",
      content:
        "Topics help you organize your study materials. Create a topic for each subject or area you're studying, then upload relevant documents to build your knowledge base.",
      learnMoreUrl: "/help/topics",
    },
    "document-upload": {
      title: "Document Upload",
      content:
        "Upload PDFs, text files, or other documents to your topic. Our AI will process them to enable Q&A and flashcard generation.",
      learnMoreUrl: "/help/documents",
    },
    "flashcard-generation": {
      title: "AI Flashcards",
      content:
        "Generate flashcards automatically from your documents using AI. Choose from basic Q&A, cloze deletion, or multiple choice formats.",
      learnMoreUrl: "/help/flashcards",
    },
    "spaced-repetition": {
      title: "Spaced Repetition",
      content:
        "Our system uses spaced repetition to optimize your learning. Cards you find difficult will appear more frequently, while easy cards appear less often.",
      learnMoreUrl: "/help/spaced-repetition",
    },
    "semantic-search": {
      title: "Semantic Search",
      content:
        "Search through your documents using natural language. Our AI understands context and meaning, not just keywords.",
      learnMoreUrl: "/help/search",
    },
    "qa-system": {
      title: "Q&A System",
      content:
        "Ask questions about your uploaded documents and get AI-powered answers based on the content. Perfect for clarifying concepts and testing understanding.",
      learnMoreUrl: "/help/qa",
    },
  };

  const help = helpContent[feature as keyof typeof helpContent];

  if (!help) {
    return (
      <HelpTooltip
        content="Help information not available for this feature."
        className={className}
      />
    );
  }

  return (
    <HelpTooltip
      title={help.title}
      content={help.content}
      learnMoreUrl={help.learnMoreUrl}
      trigger="click"
      size="lg"
      className={className}
    />
  );
}

// Help center component
interface HelpCenterProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpCenter({ isOpen, onClose }: HelpCenterProps) {
  const helpSections = [
    {
      title: "Getting Started",
      items: [
        { title: "Creating Your First Topic", href: "/help/first-topic" },
        { title: "Uploading Documents", href: "/help/upload-documents" },
        { title: "Generating Flashcards", href: "/help/generate-flashcards" },
      ],
    },
    {
      title: "Study Features",
      items: [
        { title: "Spaced Repetition System", href: "/help/spaced-repetition" },
        { title: "Q&A with AI", href: "/help/qa-system" },
        { title: "Semantic Search", href: "/help/semantic-search" },
      ],
    },
    {
      title: "Tips & Best Practices",
      items: [
        { title: "Organizing Your Topics", href: "/help/organize-topics" },
        { title: "Effective Study Strategies", href: "/help/study-strategies" },
        {
          title: "Troubleshooting Common Issues",
          href: "/help/troubleshooting",
        },
      ],
    },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BookOpen className="h-5 w-5 text-blue-600" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900">
              Help Center
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto">
          <div className="space-y-8">
            {helpSections.map((section, index) => (
              <div key={index}>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">
                  {section.title}
                </h3>
                <div className="space-y-2">
                  {section.items.map((item, itemIndex) => (
                    <a
                      key={itemIndex}
                      href={item.href}
                      className="block p-3 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{item.title}</span>
                        <ExternalLink className="h-4 w-4 text-slate-400" />
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Contact Support */}
          <div className="mt-8 pt-6 border-t border-slate-200">
            <div className="text-center">
              <h4 className="font-semibold text-slate-900 mb-2">
                Still need help?
              </h4>
              <p className="text-slate-600 mb-4">
                Can't find what you're looking for? Our support team is here to
                help.
              </p>
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                Contact Support
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HelpTooltip;
