"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { useAuth } from "@/context/auth-context";
import {
  Bell,
  Check,
  ChevronRight,
  Key,
  Lock,
  Moon,
  Palette,
  Shield,
  Sliders,
  Sun,
  User,
} from "lucide-react";
import { useTheme } from "next-themes";

export default function SettingsPage() {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();
  const [activeSection, setActiveSection] = useState<"general" | "notifications" | "security" | "integrations">("general");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          System Settings & Control
        </h1>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Configure security, notifications, theme preferences, and connected AI engines.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Navigation (4 cols) */}
        <div className="md:col-span-4 space-y-1.5">
          <button
            type="button"
            onClick={() => setActiveSection("general")}
            className={`w-full p-3 rounded-xl text-left text-xs font-semibold flex items-center justify-between transition-all ${
              activeSection === "general"
                ? "bg-brand-500/15 text-brand-600 dark:text-brand-300 border border-brand-500/30"
                : "glass-card text-gray-700 dark:text-gray-300 hover:border-black/10"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Palette className="w-4 h-4 text-brand-500" />
              <span>General & Appearance</span>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>

          <button
            type="button"
            onClick={() => setActiveSection("notifications")}
            className={`w-full p-3 rounded-xl text-left text-xs font-semibold flex items-center justify-between transition-all ${
              activeSection === "notifications"
                ? "bg-brand-500/15 text-brand-600 dark:text-brand-300 border border-brand-500/30"
                : "glass-card text-gray-700 dark:text-gray-300 hover:border-black/10"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Bell className="w-4 h-4 text-amber-500" />
              <span>Notifications & Alerts</span>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>

          <button
            type="button"
            onClick={() => setActiveSection("security")}
            className={`w-full p-3 rounded-xl text-left text-xs font-semibold flex items-center justify-between transition-all ${
              activeSection === "security"
                ? "bg-brand-500/15 text-brand-600 dark:text-brand-300 border border-brand-500/30"
                : "glass-card text-gray-700 dark:text-gray-300 hover:border-black/10"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Shield className="w-4 h-4 text-emerald-500" />
              <span>Security & Sessions</span>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>

          <button
            type="button"
            onClick={() => setActiveSection("integrations")}
            className={`w-full p-3 rounded-xl text-left text-xs font-semibold flex items-center justify-between transition-all ${
              activeSection === "integrations"
                ? "bg-brand-500/15 text-brand-600 dark:text-brand-300 border border-brand-500/30"
                : "glass-card text-gray-700 dark:text-gray-300 hover:border-black/10"
            }`}
          >
            <div className="flex items-center gap-2.5">
              <Key className="w-4 h-4 text-indigo-500" />
              <span>API Integrations & Keys</span>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        {/* Right Details Pane (8 cols) */}
        <div className="md:col-span-8 glass-card rounded-mac-lg p-6 border border-black/5 dark:border-white/5 space-y-6">
          {activeSection === "general" && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-gray-900 dark:text-white pb-2 border-b border-black/5 dark:border-white/5">
                Appearance & Preferences
              </h2>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                  Theme Mode
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setTheme("light")}
                    className={`flex-1 p-3 rounded-xl text-xs font-bold border flex items-center justify-center gap-2 transition-all ${
                      theme === "light"
                        ? "border-brand-500 bg-brand-50/50 text-brand-600"
                        : "border-gray-200 dark:border-gray-800 text-gray-500"
                    }`}
                  >
                    <Sun className="w-4 h-4" />
                    <span>Light Theme</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setTheme("dark")}
                    className={`flex-1 p-3 rounded-xl text-xs font-bold border flex items-center justify-center gap-2 transition-all ${
                      theme === "dark"
                        ? "border-brand-500 bg-brand-500/15 text-brand-400"
                        : "border-gray-200 dark:border-gray-800 text-gray-500"
                    }`}
                  >
                    <Moon className="w-4 h-4" />
                    <span>Dark Theme</span>
                  </button>
                </div>
              </div>

              <div className="pt-2">
                <label className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                  Owner Identity
                </label>
                <div className="mt-1 text-xs text-gray-500 font-mono p-3 rounded-xl bg-gray-50 dark:bg-gray-900/60 border border-black/5 dark:border-white/5">
                  {user?.name || "Ashray"} ({user?.email || "ashray@internal"})
                </div>
              </div>
            </div>
          )}

          {activeSection === "notifications" && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-gray-900 dark:text-white pb-2 border-b border-black/5 dark:border-white/5">
                Notifications & Alert Rules
              </h2>
              <div className="space-y-3 text-xs">
                <label className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-900/40">
                  <span>Pending Approval Alerts</span>
                  <input type="checkbox" defaultChecked className="rounded text-brand-600" />
                </label>
                <label className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-900/40">
                  <span>Emergency Disconnection Warnings</span>
                  <input type="checkbox" defaultChecked className="rounded text-brand-600" />
                </label>
                <label className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-900/40">
                  <span>Weekly Summary Digest</span>
                  <input type="checkbox" defaultChecked className="rounded text-brand-600" />
                </label>
              </div>
            </div>
          )}

          {activeSection === "security" && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-gray-900 dark:text-white pb-2 border-b border-black/5 dark:border-white/5">
                Security & Session Lockout
              </h2>
              <div className="text-xs text-gray-500 space-y-2">
                <p>
                  This system operates under strict single-owner authentication. Public registration is disabled by architecture.
                </p>
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-semibold">
                  Hardware Authentication Active (Current Session: Chrome / Windows)
                </div>
              </div>
            </div>
          )}

          {activeSection === "integrations" && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-gray-900 dark:text-white pb-2 border-b border-black/5 dark:border-white/5">
                API Integrations & Engine Health
              </h2>
              <div className="space-y-2.5 text-xs">
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-900/60 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-gray-900 dark:text-white">Google Gemini 2.0 Flash</div>
                    <div className="text-[11px] text-gray-400">AI Intelligence & Structured Outputs</div>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 px-2 py-0.5 rounded-full">
                    Active
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-900/60 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-gray-900 dark:text-white">Meta WhatsApp Cloud API v21.0</div>
                    <div className="text-[11px] text-gray-400">Automated Business Channel</div>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 px-2 py-0.5 rounded-full">
                    Active
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-900/60 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-gray-900 dark:text-white">Meta Instagram Messaging API v21.0</div>
                    <div className="text-[11px] text-gray-400">Automated Business DMs</div>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 px-2 py-0.5 rounded-full">
                    Active
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={handleSave}
              className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-brand-600 hover:bg-brand-500 flex items-center gap-1.5 transition-all shadow-xs"
            >
              {saved ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-300" />
                  <span>Preferences Saved</span>
                </>
              ) : (
                <span>Save Preferences</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
