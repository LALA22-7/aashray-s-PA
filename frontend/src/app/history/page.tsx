"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { ArrowDownLeft, ArrowUpRight, CheckCircle2, Clock, Filter, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface HistoryEntry {
  id: string;
  account: string;
  platform: "instagram" | "whatsapp";
  type: "inbound" | "auto_reply" | "approved_sent" | "manual_sent";
  content: string;
  contact: string;
  time: string;
}

const MOCK_HISTORY: HistoryEntry[] = [
  {
    id: "h_1",
    account: "IG (Personal)",
    platform: "instagram",
    type: "manual_sent",
    content: "Hey, are you free for a catchup this weekend?",
    contact: "@rohan_v",
    time: "Today, 8:24 PM",
  },
  {
    id: "h_2",
    account: "WA (Business)",
    platform: "whatsapp",
    type: "auto_reply",
    content: "Hi! Yes, our custom bottle advertising starts at 500 units for corporate campaigns.",
    contact: "+91 9876543210",
    time: "Today, 7:11 PM",
  },
  {
    id: "h_3",
    account: "IG (Business)",
    platform: "instagram",
    type: "approved_sent",
    content: "Approved proposal sent for 3,000 corporate wrapped bottles in Delhi.",
    contact: "@karan_events",
    time: "Today, 5:02 PM",
  },
  {
    id: "h_4",
    account: "WA (Personal)",
    platform: "whatsapp",
    type: "inbound",
    content: "Got the documents, thank you!",
    contact: "+91 9811122233",
    time: "Today, 3:45 PM",
  },
  {
    id: "h_5",
    account: "IG (Business)",
    platform: "instagram",
    type: "auto_reply",
    content: "Hey! We deliver across Mumbai, Delhi NCR, and Pune within 4-7 days.",
    contact: "@event_solutions",
    time: "Yesterday, 6:15 PM",
  },
];

export default function HistoryPage() {
  const [accountFilter, setAccountFilter] = useState("all");
  const [timeFilter, setTimeFilter] = useState("7d");

  const filtered = MOCK_HISTORY.filter((item) => {
    if (accountFilter === "all") return true;
    return item.account.toLowerCase().includes(accountFilter);
  });

  return (
    <AppShell>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-2">
            <span>Message History & Audit Logs</span>
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Complete immutable audit trail of all incoming and outgoing messages across your 4 accounts.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2">
          <select
            value={accountFilter}
            onChange={(e) => setAccountFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white dark:bg-gray-800 border border-black/5 dark:border-white/10 text-gray-900 dark:text-white"
          >
            <option value="all">All Accounts</option>
            <option value="ig (personal)">Instagram (Personal)</option>
            <option value="ig (business)">Instagram (Business)</option>
            <option value="wa (personal)">WhatsApp (Personal)</option>
            <option value="wa (business)">WhatsApp (Business)</option>
          </select>

          <select
            value={timeFilter}
            onChange={(e) => setTimeFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white dark:bg-gray-800 border border-black/5 dark:border-white/10 text-gray-900 dark:text-white"
          >
            <option value="today">Today</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </div>

      {/* History Items List */}
      <div className="glass-card rounded-mac-lg divide-y divide-black/5 dark:divide-white/5 border border-black/5 dark:border-white/5">
        {filtered.map((item) => {
          const isWA = item.platform === "whatsapp";

          return (
            <div
              key={item.id}
              className="p-4 flex items-center justify-between hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
            >
              <div className="flex items-center gap-3.5">
                <div
                  className={cn(
                    "w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-bold",
                    isWA ? "bg-emerald-600" : "bg-gradient-to-tr from-pink-500 to-purple-600"
                  )}
                >
                  {isWA ? "WA" : "IG"}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-gray-900 dark:text-white">
                      {item.account}
                    </span>
                    <span className="text-[10px] text-gray-400">({item.contact})</span>
                  </div>

                  <p className="text-xs text-gray-600 dark:text-gray-300 mt-0.5 line-clamp-1">
                    {item.content}
                  </p>
                </div>
              </div>

              <div className="text-right ml-4 shrink-0">
                <div className="text-xs font-semibold text-gray-900 dark:text-white">
                  {item.time}
                </div>
                <div className="text-[10px] font-bold text-brand-600 dark:text-brand-400 uppercase tracking-wider mt-0.5">
                  {item.type.replace("_", " ")}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </AppShell>
  );
}
