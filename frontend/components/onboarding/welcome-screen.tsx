"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  BookOpen,
  Brain,
  MessageSquare,
  Search,
  Upload,
  Sparkles,
  ArrowRight,
  Check,
  Play,
} from "lucide-react";

interface WelcomeScreenProps {
  onComplete: () => void;
  onStartTour: () => void;
  userName?: string;
}

export function WelcomeScreen({
  onComplete,
  onStartTour,
  userName,
}: WelcomeScreenProps) {
  const [currentStep, setCurrentStep] = useState(0);

  const features = [
    {
      icon: <BookOpen className="h-8 w-8 text-blue-600" />,
      title: "Organize Your Studies",
      description:
        "Create topics to organize your study materials by subject, course, or any way that works for you.",
      color: "bg-blue-50 border-blue-200",
    },
    {
      icon: <Upload className="h-8 w-8 text-green-600" />,
      title: "Upload Documents",
      description:
        "Upload PDFs, text files, and other documents. Our AI will process them to make them searchable and interactive.",
      color: "bg-green-50 border-green-200",
    },
    {
      icon: <Brain className="h-8 w-8 text-purple-600" />,
      title: "AI-Generated Flashcards",
      description:
        "Automatically generate flashcards from your documents using advanced AI. Choose from multiple formats and difficulty levels.",
      color: "bg-purple-50 border-purple-200",
    },
    {
      icon: <MessageSquare className="h-8 w-8 text-orange-600" />,
      title: "Ask Questions",
      description:
        "Get instant answers to questions about your study materials. Our AI understands context and provides detailed explanations.",
      color: "bg-orange-50 border-orange-200",
    },
    {
      icon: <Search className="h-8 w-8 text-teal-600" />,
      title: "Semantic Search",
      description:
        "Search through your documents using natural language. Find relevant information even when you don't remember exact keywords.",
      color: "bg-teal-50 border-teal-200",
    },
  ];

  const steps = [
    {
      title: `Welcome${userName ? `, ${userName}` : ""}!`,
      subtitle: "Let's get you started with your healthcare study companion",
      content: (
        <div className="text-center space-y-6">
          <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <Sparkles className="h-10 w-10 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              Welcome to Study Companion
            </h2>
            <p className="text-slate-600 max-w-md mx-auto">
              Your AI-powered study assistant for healthcare education. Let's
              explore what you can do.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Powerful Features",
      subtitle: "Everything you need to study effectively",
      content: (
        <div className="grid gap-4 md:grid-cols-2">
          {features.map((feature, index) => (
            <Card key={index} className={`${feature.color} border-2`}>
              <CardContent className="p-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">{feature.icon}</div>
                  <div>
                    <h3 className="font-semibold text-slate-900 mb-1">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-slate-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ),
    },
    {
      title: "Ready to Start?",
      subtitle: "Choose how you'd like to begin",
      content: (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="border-2 border-blue-200 hover:border-blue-300 transition-colors cursor-pointer group">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 mx-auto bg-blue-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
                  <Play className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">
                  Take the Tour
                </h3>
                <p className="text-sm text-slate-600 mb-4">
                  Get a guided walkthrough of all the features and learn how to
                  use them effectively.
                </p>
                <Button
                  onClick={onStartTour}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  Start Tour
                </Button>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-200 hover:border-green-300 transition-colors cursor-pointer group">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
                  <ArrowRight className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">
                  Jump Right In
                </h3>
                <p className="text-sm text-slate-600 mb-4">
                  Skip the tour and start creating your first topic. You can
                  always access help later.
                </p>
                <Button
                  onClick={onComplete}
                  variant="outline"
                  className="w-full border-green-600 text-green-600 hover:bg-green-50"
                >
                  Get Started
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="text-center">
            <p className="text-sm text-slate-500">
              You can always access the tour and help from the menu later.
            </p>
          </div>
        </div>
      ),
    },
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const currentStepData = steps[currentStep];

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <Card className="shadow-xl border-0 bg-white/95 backdrop-blur-sm">
          <CardContent className="p-8 md:p-12">
            {/* Progress Indicator */}
            <div className="flex items-center justify-center mb-8">
              <div className="flex space-x-2">
                {steps.map((_, index) => (
                  <div
                    key={index}
                    className={`w-3 h-3 rounded-full transition-colors ${
                      index === currentStep
                        ? "bg-blue-600"
                        : index < currentStep
                        ? "bg-blue-300"
                        : "bg-slate-200"
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-slate-900 mb-2">
                {currentStepData.title}
              </h1>
              <p className="text-slate-600">{currentStepData.subtitle}</p>
            </div>

            {/* Content */}
            <div className="mb-8">{currentStepData.content}</div>

            {/* Navigation */}
            {currentStep < steps.length - 1 && (
              <div className="flex items-center justify-between">
                <Button
                  onClick={handlePrevious}
                  variant="outline"
                  disabled={currentStep === 0}
                  className="flex items-center space-x-2"
                >
                  <span>Previous</span>
                </Button>

                <div className="flex items-center space-x-4">
                  <Button
                    onClick={onComplete}
                    variant="ghost"
                    className="text-slate-500"
                  >
                    Skip
                  </Button>

                  <Button
                    onClick={handleNext}
                    className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
                  >
                    <span>Next</span>
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Hook to manage welcome screen state
export function useWelcomeScreen() {
  const [showWelcome, setShowWelcome] = useState(false);

  const checkShouldShow = () => {
    const hasSeenWelcome = localStorage.getItem("welcome-completed");
    const hasTopics = localStorage.getItem("user-has-topics");

    return !hasSeenWelcome && !hasTopics;
  };

  const completeWelcome = () => {
    localStorage.setItem("welcome-completed", "true");
    setShowWelcome(false);
  };

  const showWelcomeScreen = () => {
    setShowWelcome(true);
  };

  const resetWelcome = () => {
    localStorage.removeItem("welcome-completed");
    setShowWelcome(true);
  };

  return {
    showWelcome,
    checkShouldShow,
    completeWelcome,
    showWelcomeScreen,
    resetWelcome,
  };
}

export default WelcomeScreen;
