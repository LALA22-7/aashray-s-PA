"use client";

import React from "react";
import Link from "next/navigation";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Bot,
  CheckCircle2,
  Clock,
  Inbox,
  Layers,
  LayoutDashboard,
  Settings,
  ShieldAlert,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: number;
}

const NAV_ITEMS: NavItem[] = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Inbox", href: "/inbox", icon: Inbox, badge: 12 },
  { name: "Approvals", href: "/approvals", icon: CheckCircle2, badge: 5 },
  { name: "Accounts", href: "/accounts", icon: Layers },
  { name: "AI Assistants", href: "/assistants", icon: Bot },
  { name: "History", href: "/history", icon: Clock },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-64 h-screen sticky top-0 border-r border-black/5 dark:border-white/5 bg-white/70 dark:bg-[#12151D]/70 backdrop-blur-xl z-30 select-none">
      {/* Top Branding */}
      <div className="p-5 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 font-bold text-lg">
            A
          </div>
          <div>
            <div className="font-bold text-base tracking-tight text-gray-900 dark:text-white leading-tight">
              Aashray&apos;sPA
            </div>
            <div className="text-[11px] font-medium text-gray-500 dark:text-gray-400">
              Personal Command Centre
            </div>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const isActive =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <a
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-tight transition-all",
                isActive
                  ? "bg-brand-50 dark:bg-brand-500/15 text-brand-700 dark:text-brand-300 shadow-xs"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5"
              )}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive
                      ? "text-brand-600 dark:text-brand-400"
                      : "text-gray-400 dark:text-gray-500"
                  )}
                />
                <span>{item.name}</span>
              </div>
              {item.badge !== undefined && (
                <span
                  className={cn(
                    "px-2 py-0.5 text-[10px] font-bold rounded-full",
                    isActive
                      ? "bg-brand-200/60 dark:bg-brand-400/20 text-brand-800 dark:text-brand-200"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                  )}
                >
                  {item.badge}
                </span>
              )}
            </a>
          );
        })}
      </nav>

      {/* Bottom Status Card */}
      <div className="p-4 border-t border-black/5 dark:border-white/5">
        <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-900/60 border border-black/5 dark:border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <div className="text-[11px] font-semibold text-gray-700 dark:text-gray-300">
              4 Accounts Active
            </div>
          </div>
          <span className="text-[10px] text-gray-400 font-medium">v0.1.0</span>
        </div>
      </div>
    </aside>
  );
}

