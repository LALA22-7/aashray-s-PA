"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { ArrowUpRight, BarChart3, TrendingUp, Users } from "lucide-react";

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("7d");

  return (
    <AppShell>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-2">
            <span>Analytics & Intelligence</span>
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Real-time communication throughput, AI dispatch rates, and response metrics.
          </p>
        </div>

        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="self-start sm:self-auto px-3 py-1.5 rounded-xl text-xs font-semibold bg-white dark:bg-gray-800 border border-black/5 dark:border-white/10 text-gray-900 dark:text-white"
        >
          <option value="today">Today</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>
      </div>

      {/* 3 Analytics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="glass-card rounded-mac p-5">
          <div className="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white">
            412
          </div>
          <div className="text-xs font-semibold text-gray-500 mt-1">Total Messages Handled</div>
          <div className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 mt-2">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>+24% from last period</span>
          </div>
        </div>

        <div className="glass-card rounded-mac p-5">
          <div className="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white">
            96%
          </div>
          <div className="text-xs font-semibold text-gray-500 mt-1">AI Automation Rate</div>
          <div className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 mt-2">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>+6% accuracy</span>
          </div>
        </div>

        <div className="glass-card rounded-mac p-5">
          <div className="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white">
            28
          </div>
          <div className="text-xs font-semibold text-gray-500 mt-1">Human Approvals Reviewed</div>
          <div className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 mt-2">
            <span>Avg response time: 1.2s</span>
          </div>
        </div>
      </div>

      {/* Beautiful Curve Wave Chart matching the design mockup */}
      <div className="glass-card rounded-mac-lg p-6 border border-black/5 dark:border-white/5 space-y-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-wider">
            Volume & Activity Waveform
          </div>
          <span className="text-[11px] text-gray-400 font-medium">Messages per Day</span>
        </div>

        <div className="w-full h-44 relative">
          <svg
            viewBox="0 0 500 150"
            className="w-full h-full overflow-visible"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#818CF8" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#818CF8" stopOpacity="0.0" />
              </linearGradient>
            </defs>
            {/* Fill under curve */}
            <path
              d="M 0 120 Q 80 40, 160 85 T 320 50 T 500 70 L 500 150 L 0 150 Z"
              fill="url(#chartGradient)"
            />
            {/* Line stroke */}
            <path
              d="M 0 120 Q 80 40, 160 85 T 320 50 T 500 70"
              fill="none"
              stroke="#6366F1"
              strokeWidth="3"
            />
          </svg>
        </div>

        <div className="flex justify-between text-[11px] text-gray-400 font-medium pt-2 border-t border-black/5 dark:border-white/5">
          <span>Mon</span>
          <span>Tue</span>
          <span>Wed</span>
          <span>Thu</span>
          <span>Fri</span>
          <span>Sat</span>
          <span>Sun</span>
        </div>
      </div>
    </AppShell>
  );
}
