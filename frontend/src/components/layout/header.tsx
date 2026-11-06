"use client";

import React, { useState } from "react";
import { useTheme } from "next-themes";
import { useAuth } from "@/context/auth-context";
import {
  Bell,
  LogOut,
  Moon,
  Search,
  Sun,
  User as UserIcon,
} from "lucide-react";

interface HeaderProps {
  onSearchClick?: () => void;
}

export function Header({ onSearchClick }: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <header className="sticky top-0 z-20 h-14 border-b border-black/5 dark:border-white/5 bg-white/60 dark:bg-[#0B0D13]/60 backdrop-blur-xl px-4 md:px-6 flex items-center justify-between">
      {/* Left: macOS dots & title */}
      <div className="flex items-center gap-4">
        {/* macOS window control dots */}
        <div className="hidden md:flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-[#FF5F56] border border-[#E0443E]/50" />
          <span className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-[#DEA123]/50" />
          <span className="w-3 h-3 rounded-full bg-[#27C93F] border border-[#1AAB29]/50" />
        </div>

        <div className="text-xs font-semibold text-gray-500 dark:text-gray-400">
          Aashray&apos;sPA <span className="text-gray-300 dark:text-gray-600">/</span>{" "}
          <span className="text-gray-900 dark:text-white font-bold">Pro Plan</span>
        </div>
      </div>

      {/* Middle: Global Search Input */}
      <div className="flex-1 max-w-md mx-4 hidden sm:block">
        <button
          type="button"
          onClick={onSearchClick}
          className="w-full flex items-center justify-between px-3 py-1.5 rounded-xl text-xs bg-gray-100/70 dark:bg-gray-900/60 border border-black/5 dark:border-white/5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-all"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5" />
            <span>Search conversations, accounts, or commands...</span>
          </div>
          <kbd className="px-1.5 py-0.5 text-[10px] font-semibold bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded shadow-xs text-gray-500">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Theme Toggle */}
        <button
          type="button"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="w-8 h-8 rounded-xl flex items-center justify-center text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          title="Toggle Light/Dark Theme"
        >
          {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-8 h-8 rounded-xl flex items-center justify-center text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 transition-colors relative"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-brand-500" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-72 rounded-2xl glass-card p-3 shadow-xl z-50">
              <div className="text-xs font-bold text-gray-900 dark:text-white mb-2 pb-1 border-b border-black/5 dark:border-white/5 flex items-center justify-between">
                <span>Notifications</span>
                <span className="text-[10px] text-brand-600 font-semibold cursor-pointer">Mark all read</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="p-2 rounded-xl bg-brand-50/50 dark:bg-brand-500/10 border border-brand-200/50 dark:border-brand-500/20">
                  <div className="font-semibold text-gray-900 dark:text-white">5 Pending Approvals</div>
                  <div className="text-gray-500 text-[11px]">Instagram Business & WhatsApp enquiries require review.</div>
                </div>
                <div className="p-2 rounded-xl bg-gray-50 dark:bg-gray-800/40">
                  <div className="font-semibold text-gray-900 dark:text-white">Auto-reply sent</div>
                  <div className="text-gray-500 text-[11px]">Instagram Personal replied to Rohan V.</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Profile Avatar / Menu */}
        <div className="relative ml-1">
          <button
            type="button"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2 p-1 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-brand-600 to-indigo-500 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              {user?.name?.[0] || "A"}
            </div>
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-xl glass-card p-1.5 shadow-xl z-50">
              <div className="px-3 py-2 border-b border-black/5 dark:border-white/5">
                <div className="font-bold text-xs text-gray-900 dark:text-white">{user?.name || "Ashray"}</div>
                <div className="text-[10px] text-gray-400 truncate">{user?.email || "ashray@internal"}</div>
              </div>
              <button
                type="button"
                onClick={logout}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

