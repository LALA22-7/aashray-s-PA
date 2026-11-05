"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Bot,
  CheckCircle2,
  Clock,
  Inbox,
  Layers,
  LayoutDashboard,
  Menu,
  Settings,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function MobileNav() {
  const pathname = usePathname();
  const [showMore, setShowMore] = useState(false);

  const primaryItems = [
    { name: "Home", href: "/", icon: LayoutDashboard },
    { name: "Inbox", href: "/inbox", icon: Inbox, badge: 12 },
    { name: "Approvals", href: "/approvals", icon: CheckCircle2, badge: 5 },
    { name: "History", href: "/history", icon: Clock },
  ];

  const moreItems = [
    { name: "Accounts", href: "/accounts", icon: Layers, desc: "Connected platforms" },
    { name: "AI Assistants", href: "/assistants", icon: Bot, desc: "Tone, prompts & rules" },
    { name: "Analytics", href: "/analytics", icon: BarChart3, desc: "Volume & reply rates" },
    { name: "Settings", href: "/settings", icon: Settings, desc: "Preferences & security" },
  ];

  return (
    <>
      {/* Bottom Floating Bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-30 border-t border-black/5 dark:border-white/5 bg-white/85 dark:bg-[#10131B]/85 backdrop-blur-xl px-2 py-1.5 flex items-center justify-around safe-area-bottom">
        {primaryItems.map((item) => {
          const isActive = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <a
              key={item.name}
              href={item.href}
              className={cn(
                "flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all relative",
                isActive ? "text-brand-600 dark:text-brand-400 font-bold" : "text-gray-500 dark:text-gray-400"
              )}
            >
              <div className="relative">
                <Icon className="w-5 h-5" />
                {item.badge && (
                  <span className="absolute -top-1.5 -right-2 px-1 text-[9px] font-bold bg-brand-500 text-white rounded-full min-w-3.5 h-3.5 flex items-center justify-center">
                    {item.badge}
                  </span>
                )}
              </div>
              <span className="text-[10px] mt-0.5 tracking-tight">{item.name}</span>
            </a>
          );
        })}

        {/* More Toggle */}
        <button
          type="button"
          onClick={() => setShowMore(true)}
          className="flex flex-col items-center justify-center py-1 px-3 rounded-xl text-gray-500 dark:text-gray-400"
        >
          <Menu className="w-5 h-5" />
          <span className="text-[10px] mt-0.5 tracking-tight">More</span>
        </button>
      </nav>

      {/* More Drawer Sheet */}
      {showMore && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex flex-col justify-end">
          <div className="w-full rounded-t-3xl glass-card p-5 pb-8 animate-in slide-in-from-bottom duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-black/5 dark:border-white/5">
              <span className="font-bold text-sm text-gray-900 dark:text-white">Management Sections</span>
              <button
                type="button"
                onClick={() => setShowMore(false)}
                className="w-7 h-7 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 mt-4">
              {moreItems.map((m) => {
                const Icon = m.icon;
                return (
                  <a
                    key={m.name}
                    href={m.href}
                    onClick={() => setShowMore(false)}
                    className="p-3 rounded-2xl bg-gray-50/80 dark:bg-gray-900/60 border border-black/5 dark:border-white/5 flex flex-col gap-1 hover:border-brand-500/30 transition-all"
                  >
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400">
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="font-bold text-xs text-gray-900 dark:text-white">{m.name}</span>
                    </div>
                    <span className="text-[10px] text-gray-400 mt-1">{m.desc}</span>
                  </a>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
