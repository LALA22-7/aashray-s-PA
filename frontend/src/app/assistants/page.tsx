"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { apiClient } from "@/lib/api";
import { Assistant, BusinessKnowledgeItem } from "@/types";
import {
  ArrowRight,
  Bot,
  Check,
  ChevronRight,
  Save,
  Sliders,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function AssistantsPage() {
  const [assistants, setAssistants] = useState<Assistant[]>([]);
  const [activeAssistant, setActiveAssistant] = useState<Assistant | null>(null);
  const [instructions, setInstructions] = useState("");
  const [tone, setTone] = useState("Professional");
  const [autoReply, setAutoReply] = useState(false);
  const [hinglish, setHinglish] = useState(0.5);
  const [emoji, setEmoji] = useState(0.3);
  const [knowledge, setKnowledge] = useState<BusinessKnowledgeItem[]>([]);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    async function loadData() {
      const [astList, kList] = await Promise.all([
        apiClient.getAssistants(),
        apiClient.getKnowledge(),
      ]);
      setAssistants(astList);
      setKnowledge(kList);
      if (astList.length > 0 && !activeAssistant) {
        selectAssistant(astList[1]); // default to IG - Business
      }
    }
    loadData();
  }, [activeAssistant]);

  const selectAssistant = (ast: Assistant) => {
    setActiveAssistant(ast);
    setInstructions(ast.system_instruction);
    setTone(ast.tone);
    setAutoReply(ast.autonomy_mode === "automatic");
    setHinglish(ast.hinglish_preference);
    setEmoji(ast.emoji_usage);
  };

  const handleSave = async () => {
    if (!activeAssistant) return;
    await apiClient.updateAssistant(activeAssistant.id, {
      system_instruction: instructions,
      tone,
      autonomy_mode: autoReply ? "automatic" : "approval",
      hinglish_preference: hinglish,
      emoji_usage: emoji,
    });
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-2">
          <span>AI Assistants Management</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
        </h1>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Each social account is powered by an independent persona, customizable prompt guidelines, and response rules.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: 4 Assistant Cards (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
            4 Account Personas
          </div>

          {assistants.map((ast) => {
            const isSelected = activeAssistant?.id === ast.id;
            const isWA = ast.platform === "whatsapp";

            return (
              <button
                key={ast.id}
                type="button"
                onClick={() => selectAssistant(ast)}
                className={cn(
                  "w-full glass-card rounded-mac p-4 text-left flex items-center justify-between transition-all block",
                  isSelected
                    ? "border-brand-500/80 bg-brand-50/50 dark:bg-brand-500/15 shadow-md"
                    : "hover:border-black/10 dark:hover:border-white/10"
                )}
              >
                <div className="flex items-center gap-3.5">
                  <div
                    className={cn(
                      "w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-xs shrink-0",
                      isWA
                        ? "bg-emerald-600"
                        : "bg-gradient-to-tr from-pink-500 to-purple-600"
                    )}
                  >
                    {isWA ? "WA" : "IG"}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900 dark:text-white">
                      {ast.account_name}
                    </div>
                    <div className="text-[11px] text-gray-500 dark:text-gray-400 font-medium">
                      {ast.personality_summary}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      "px-2 py-0.5 rounded-md text-[10px] font-bold uppercase",
                      ast.autonomy_mode === "automatic"
                        ? "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600"
                        : "bg-amber-50 dark:bg-amber-500/10 text-amber-600"
                    )}
                  >
                    {ast.autonomy_mode}
                  </span>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </div>
              </button>
            );
          })}

          {/* Business Knowledge Card */}
          <div className="mt-6 p-4 rounded-mac glass-card border border-black/5 dark:border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-900 dark:text-white">
                Verified Bottle Knowledge Base
              </span>
              <span className="text-[10px] font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-500/10 px-2 py-0.5 rounded-full">
                {knowledge.length} Items Active
              </span>
            </div>
            <div className="text-[11px] text-gray-500 space-y-2">
              {knowledge.map((k) => (
                <div key={k.id} className="p-2 rounded-lg bg-gray-50 dark:bg-gray-800/40">
                  <div className="font-semibold text-gray-800 dark:text-gray-200">{k.title}</div>
                  <div className="text-[10px] text-gray-400 mt-0.5 line-clamp-1">{k.content}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Detailed Assistant Settings (7 cols) */}
        <div className="lg:col-span-7">
          {activeAssistant ? (
            <div className="glass-card rounded-mac-lg p-6 border border-black/5 dark:border-white/5 space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-black/5 dark:border-white/5">
                <div>
                  <h2 className="text-base font-bold text-gray-900 dark:text-white">
                    {activeAssistant.account_name} Assistant
                  </h2>
                  <p className="text-xs text-gray-500">
                    Fine-tune system instructions and response behaviors.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleSave}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 shadow-sm flex items-center gap-1.5 transition-all"
                >
                  {savedSuccess ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-300" />
                      <span>Saved!</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-3.5 h-3.5" />
                      <span>Save Changes</span>
                    </>
                  )}
                </button>
              </div>

              {/* Instructions Textarea */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  System Instructions & Prompt Guidelines
                </label>
                <textarea
                  rows={4}
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Describe how the assistant should respond, tone, boundaries, and what it must never say..."
                  className="w-full p-3.5 rounded-xl text-xs bg-white/70 dark:bg-gray-900/70 border border-black/10 dark:border-white/10 text-gray-900 dark:text-white leading-relaxed focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
                <p className="text-[11px] text-gray-400">
                  Changes take effect immediately on next inbound webhook or manual generation.
                </p>
              </div>

              {/* Tone Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  Communication Tone
                </label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full p-2.5 rounded-xl text-xs bg-white/70 dark:bg-gray-900/70 border border-black/10 dark:border-white/10 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="Professional & Brand">Professional & Brand (Concise, Polished)</option>
                  <option value="Friendly & Casual">Friendly & Casual (Warm, Conversational)</option>
                  <option value="Personal & Smart">Personal & Smart (Thoughtful, Authentic)</option>
                  <option value="Formal & Sales">Formal & Sales (Business Executive)</option>
                </select>
              </div>

              {/* Autonomy Mode Switch */}
              <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900/40 border border-black/5 dark:border-white/5 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-gray-900 dark:text-white">
                    Auto-Reply Permission
                  </div>
                  <div className="text-[11px] text-gray-500 dark:text-gray-400">
                    {autoReply
                      ? "High-confidence replies are automatically dispatched."
                      : "Require owner sign-off on all replies via the Approval Centre."}
                  </div>
                </div>

                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoReply}
                    onChange={(e) => setAutoReply(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-600"></div>
                </label>
              </div>

              {/* Sliders: Hinglish & Emoji */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold text-gray-700 dark:text-gray-300">Hinglish Mixture</span>
                    <span className="text-brand-600 font-bold">{Math.round(hinglish * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={hinglish}
                    onChange={(e) => setHinglish(parseFloat(e.target.value))}
                    className="w-full accent-brand-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-gray-400">
                    <span>Pure English</span>
                    <span>High Hinglish</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold text-gray-700 dark:text-gray-300">Emoji Usage</span>
                    <span className="text-brand-600 font-bold">{Math.round(emoji * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={emoji}
                    onChange={(e) => setEmoji(parseFloat(e.target.value))}
                    className="w-full accent-brand-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-gray-400">
                    <span>Minimal</span>
                    <span>Expressive</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card rounded-mac p-12 text-center text-xs text-gray-400">
              Select an assistant to inspect or edit its configuration.
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

