import * as React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
  variant?: "default" | "primary" | "success" | "warning" | "error";
}

const variantStyles = {
  default: "bg-white/80 border-white/20",
  primary: "bg-blue-50/80 border-blue-200/50 text-blue-900",
  success: "bg-green-50/80 border-green-200/50 text-green-900",
  warning: "bg-yellow-50/80 border-yellow-200/50 text-yellow-900",
  error: "bg-red-50/80 border-red-200/50 text-red-900",
};

const iconStyles = {
  default: "text-gray-600",
  primary: "text-blue-600",
  success: "text-green-600",
  warning: "text-yellow-600",
  error: "text-red-600",
};

export function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  className,
  variant = "default",
}: StatsCardProps) {
  return (
    <Card
      className={cn(
        "backdrop-blur-sm hover:shadow-lg transition-all duration-200 hover:scale-[1.02]",
        variantStyles[variant],
        className
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
            <div className="flex items-baseline gap-2">
              <p className="text-2xl font-bold">{value}</p>
              {trend && (
                <span
                  className={cn(
                    "text-xs font-medium px-2 py-1 rounded-full",
                    trend.isPositive
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  )}
                >
                  {trend.isPositive ? "+" : ""}
                  {trend.value}%
                </span>
              )}
            </div>
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
          {Icon && (
            <div
              className={cn(
                "p-3 rounded-full bg-white/50",
                iconStyles[variant]
              )}
            >
              <Icon className="h-6 w-6" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default StatsCard;
