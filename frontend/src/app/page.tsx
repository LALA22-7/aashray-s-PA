"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/context/auth-context";
import { AppShell } from "@/components/layout/app-shell";
import { apiClient } from "@/lib/api";
import { MetricSummary, RecentActivityItem, SocialAccount } from "@/types";
import {
  ArrowRight,
  BarChart2,
  Calendar,
  CheckCircle2,
  Clock,
  Layers,
  MessageSquare,
  ShieldAlert,
} from "lucide-react";
import { formatTimeAgo } from "@/lib/utils";

export default function DashboardOverviewPage() {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<MetricSummary | null>(null);
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [activities, setActivities] = useState<RecentActivityItem[]>([]);
  const [emergencyActive, setEmergencyActive] = useState(false);
  const [isStopping, setIsStopping] = useState(false);

  useEffect(() => {
    async function loadData() {
      const [m, a, act] = await Promise.all([
        apiClient.getMetrics(),
        apiClient.getAccounts(),
        apiClient.getRecentActivity(),
      ]);
      setMetrics(m);
      setAccounts(a);
      setActivities(act);
      const isPaused = a.every((acc) => acc.automation_status === "paused" || acc.automation_mode === "disabled");
      setEmergencyActive(isPaused);
    }
    loadData();
  }, []);

  const handleToggleEmergency = async () => {
    setIsStopping(true);
    if (!emergencyActive) {
      await apiClient.triggerEmergencyStop();
      setEmergencyActive(true);
    } else {
      await apiClient.resumeAutomation();
      setEmergencyActive(false);
    }
    const updatedAccounts = await apiClient.getAccounts();
    setAccounts(updatedAccounts);
    setIsStopping(false);
  };

  const todayFormatted = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date());

  return (
    <AppShell>
      {/* Emergency Stop Alert Banner if active */}
      {emergencyActive && (
        <div className="mb-6 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-700 dark:text-amber-300 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-500" />
            <div>
              <div className="text-xs font-bold">EMERGENCY AUTOMATION PAUSE ACTIVE</div>
              <div className="text-[11px] opacity-80">
                All automatic outbound messaging is safely halted. Replies require manual sign-off.
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={handleToggleEmergency}
            disabled={isStopping}
            className="px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-500 text-white hover:bg-amber-600 transition-all shadow-xs"
          >
            {isStopping ? "Updating..." : "Resume Automation"}
          </button>
        </div>
      )}

      {/* Top Greeting & Date */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white flex items-center gap-2">
            <span>Good Evening, {user?.name || "Ashray"}</span>
            <span className="text-2xl">👋</span>
          </h1>
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1">
            Here&apos;s what&apos;s happening across your accounts today.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl glass-card text-xs font-medium text-gray-600 dark:text-gray-300">
            <Calendar className="w-3.5 h-3.5 text-gray-400" />
            <span>{todayFormatted}</span>
          </div>

          <button
            type="button"
            onClick={handleToggleEmergency}
            disabled={isStopping}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-xs ${
              emergencyActive
                ? "bg-emerald-500 text-white hover:bg-emerald-600"
                : "bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20 hover:bg-red-500 hover:text-white"
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{emergencyActive ? "Resume Safe AI" : "Emergency Stop"}</span>
          </button>
        </div>
      </div>

      {/* 4 Summary Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        {/* Metric 1 */}
        <div className="glass-card rounded-mac p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
              {metrics?.connected_accounts ?? 4}
            </div>
            <div className="text-[11px] sm:text-xs font-medium text-gray-500 dark:text-gray-400 mt-0.5">
              Connected Accounts
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
        </div>

        {/* Metric 2 */}
        <div className="glass-card rounded-mac p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
              {metrics?.messages_handled ?? 38}
            </div>
            <div className="text-[11px] sm:text-xs font-medium text-gray-500 dark:text-gray-400 mt-0.5">
              Messages Handled
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
            <MessageSquare className="w-5 h-5" />
          </div>
        </div>

        {/* Metric 3 */}
        <a
          href="/approvals"
          className="glass-card rounded-mac p-4 sm:p-5 flex items-center justify-between hover:border-amber-500/30 transition-all group"
        >
          <div>
            <div className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">
              {metrics?.pending_approvals ?? 12}
            </div>
            <div className="text-[11px] sm:text-xs font-medium text-gray-500 dark:text-gray-400 mt-0.5">
              Pending Approvals
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
        </a>

        {/* Metric 4 */}
        <div className="glass-card rounded-mac p-4 sm:p-5 flex items-center justify-between">
          <div>
            <div className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
              {metrics?.auto_reply_rate ?? 96}%
            </div>
            <div className="text-[11px] sm:text-xs font-medium text-gray-500 dark:text-gray-400 mt-0.5">
              Auto-Reply Rate
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-sky-50 dark:bg-sky-500/10 text-sky-600 dark:text-sky-400 flex items-center justify-center">
            <BarChart2 className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Two Column Section: Accounts & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Accounts Overview */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-sm font-bold text-gray-900 dark:text-white tracking-tight">
              Accounts
            </h2>
            <a
              href="/accounts"
              className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
          </div>

          <div className="space-y-2.5">
            {accounts.map((acc) => (
              <a
                key={acc.id}
                href="/accounts"
                className="glass-card rounded-mac p-3.5 sm:p-4 flex items-center justify-between hover:border-brand-500/30 transition-all block group"
              >
                <div className="flex items-center gap-3.5">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-xs ${
                      acc.platform === "instagram"
                        ? "bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600"
                        : "bg-gradient-to-tr from-emerald-500 to-green-600"
                    }`}
                  >
                    {acc.platform === "instagram" ? "IG" : "WA"}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                      {acc.display_name}
                    </div>
                    <div className="text-[11px] text-gray-400 font-mono mt-0.5">
                      {acc.platform_account_id}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>Active</span>
                  </span>
                </div>
              </a>
            ))}
          </div>
        </div>

        {/* Right: Recent Activity */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-sm font-bold text-gray-900 dark:text-white tracking-tight">
              Recent Activity
            </h2>
            <div className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>Live</span>
            </div>
          </div>

          <div className="space-y-2.5">
            {activities.map((act) => (
              <div
                key={act.id}
                className="glass-card rounded-mac p-3.5 sm:p-4 flex items-center justify-between"
              >
                <div className="flex items-center gap-3.5">
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-bold ${
                      act.platform === "instagram"
                        ? "bg-gradient-to-tr from-pink-500 to-rose-600"
                        : "bg-emerald-600"
                    }`}
                  >
                    {act.platform === "instagram" ? "IG" : "WA"}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900 dark:text-white">
                      {act.description}
                    </div>
                    <div className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-1">
                      {act.snippet}
                    </div>
                  </div>
                </div>

                <div className="text-[11px] text-gray-400 font-medium whitespace-nowrap ml-2">
                  {formatTimeAgo(act.timestamp)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

