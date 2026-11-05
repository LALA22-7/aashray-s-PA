"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { apiClient } from "@/lib/api";
import { SocialAccount } from "@/types";
import {
  Check,
  CheckCircle2,
  ExternalLink,
  Layers,
  Plus,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import { cn, formatTimeAgo } from "@/lib/utils";

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    async function loadAccounts() {
      const data = await apiClient.getAccounts();
      setAccounts(data);
    }
    loadAccounts();
  }, []);

  const handleModeChange = async (
    accountId: string,
    mode: "disabled" | "approval" | "automatic"
  ) => {
    setUpdatingId(accountId);
    await apiClient.updateAccountAutomation(accountId, mode);
    const updated = await apiClient.getAccounts();
    setAccounts(updated);
    setUpdatingId(null);
  };

  return (
    <AppShell>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-2">
            <span>Connected Accounts</span>
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            4 independent accounts belonging to Ashray, managed through isolated AI channels.
          </p>
        </div>

        <button
          type="button"
          onClick={() => alert("All 4 production accounts are registered and connected.")}
          className="self-start sm:self-auto px-4 py-2 rounded-xl text-xs font-bold text-white bg-brand-600 hover:bg-brand-500 shadow-sm flex items-center gap-1.5 transition-all"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Account</span>
        </button>
      </div>

      {/* Accounts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {accounts.map((acc) => {
          const isWA = acc.platform === "whatsapp";

          return (
            <div
              key={acc.id}
              className="glass-card rounded-mac-lg p-5 border border-black/5 dark:border-white/5 space-y-4 shadow-sm"
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "w-11 h-11 rounded-2xl flex items-center justify-center text-white font-bold text-sm shadow-xs",
                      isWA
                        ? "bg-gradient-to-tr from-emerald-500 to-green-600"
                        : "bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600"
                    )}
                  >
                    {isWA ? "WA" : "IG"}
                  </div>
                  <div>
                    <div className="text-sm font-bold text-gray-900 dark:text-white">
                      {acc.display_name}
                    </div>
                    <div className="text-xs text-gray-400 font-mono mt-0.5">
                      {acc.platform_account_id}
                    </div>
                  </div>
                </div>

                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  <span>Connected</span>
                </span>
              </div>

              {/* Status & Sync Meta */}
              <div className="grid grid-cols-2 gap-2 text-xs py-2 border-y border-black/5 dark:border-white/5">
                <div>
                  <span className="text-gray-400 text-[11px]">Integration:</span>
                  <div className="font-semibold text-gray-800 dark:text-gray-200">
                    {acc.account_type === "business" ? "Official Meta API" : "AI Manual Workflow"}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400 text-[11px]">Last Sync:</span>
                  <div className="font-semibold text-gray-800 dark:text-gray-200">
                    {formatTimeAgo(acc.last_sync_at || new Date().toISOString())}
                  </div>
                </div>
              </div>

              {/* Automation Mode Switcher */}
              <div className="flex items-center justify-between pt-1">
                <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                  Operating Mode
                </div>
                <select
                  disabled={updatingId === acc.id}
                  value={acc.automation_mode}
                  onChange={(e) =>
                    handleModeChange(acc.id, e.target.value as "disabled" | "approval" | "automatic")
                  }
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-gray-100 dark:bg-gray-800 border border-black/5 dark:border-white/10 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
                >
                  <option value="automatic">Automatic (Direct Send)</option>
                  <option value="approval">Approval (Require Sign-off)</option>
                  <option value="disabled">Manual (Disabled)</option>
                </select>
              </div>
            </div>
          );
        })}
      </div>
    </AppShell>
  );
}
