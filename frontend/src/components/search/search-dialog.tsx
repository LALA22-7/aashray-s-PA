"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  BarChart3,
  Bot,
  CheckCircle2,
  Clock,
  Inbox,
  Layers,
  LayoutDashboard,
  Search,
  Settings,
  X,
} from "lucide-react";

interface SearchDialogProps {
  open: boolean;
  onClose: () => void;
}

export function SearchDialog({ open, onClose }: SearchDialogProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  if (!open) return null;

  const quickLinks = [
    { label: "Overview", href: "/", icon: LayoutDashboard, category: "Navigation" },
    { label: "Unified Inbox", href: "/inbox", icon: Inbox, category: "Navigation" },
    { label: "Review Approvals (5)", href: "/approvals", icon: CheckCircle2, category: "Action" },
    { label: "AI Assistants", href: "/assistants", icon: Bot, category: "Configuration" },
    { label: "Connected Accounts", href: "/accounts", icon: Layers, category: "Configuration" },
    { label: "Message History & Logs", href: "/history", icon: Clock, category: "Audit" },
    { label: "Analytics & Performance", href: "/analytics", icon: BarChart3, category: "Reports" },
    { label: "System Settings", href: "/settings", icon: Settings, category: "Settings" },
  ];

  const filtered = quickLinks.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (href: string) => {
    onClose();
    router.push(href);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-start justify-center pt-20 p-4">
      <div className="w-full max-w-lg rounded-2xl glass-card shadow-2xl border border-black/10 dark:border-white/10 overflow-hidden animate-in fade-in-0 zoom-in-95 duration-150">
        {/* Input Bar */}
        <div className="p-3.5 border-b border-black/5 dark:border-white/5 flex items-center gap-3">
          <Search className="w-4 h-4 text-gray-400 ml-1" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command, search accounts, or jump to..."
            className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none"
          />
          <button
            type="button"
            onClick={onClose}
            className="w-6 h-6 rounded-md hover:bg-black/5 dark:hover:bg-white/5 flex items-center justify-center text-gray-400 hover:text-gray-600"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Results */}
        <div className="p-2 max-h-80 overflow-y-auto space-y-1">
          {filtered.length > 0 ? (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.label}
                  type="button"
                  onClick={() => handleSelect(item.href)}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl text-left hover:bg-brand-50 dark:hover:bg-brand-500/15 transition-all text-gray-700 dark:text-gray-200 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 group-hover:bg-brand-500/20 text-gray-500 group-hover:text-brand-600 transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-semibold">{item.label}</span>
                  </div>
                  <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">
                    {item.category}
                  </span>
                </button>
              );
            })
          ) : (
            <div className="py-8 text-center text-xs text-gray-400">
              No results found for &ldquo;{query}&rdquo;
            </div>
          )}
        </div>

        {/* Footer tip */}
        <div className="px-4 py-2 border-t border-black/5 dark:border-white/5 bg-gray-50/50 dark:bg-gray-900/40 text-[11px] text-gray-400 flex items-center justify-between">
          <span>Navigate with arrow keys</span>
          <span>ESC to close</span>
        </div>
      </div>
    </div>
  );
}
