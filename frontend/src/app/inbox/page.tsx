"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { apiClient } from "@/lib/api";
import { Conversation, Message } from "@/types";
import { Check, Copy, MessageSquare, Send, Sparkles, User } from "lucide-react";
import { cn, formatTimeAgo } from "@/lib/utils";

export default function InboxPage() {
  const [filter, setFilter] = useState<"all" | "instagram" | "whatsapp">("all");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [replyText, setReplyText] = useState("");
  const [copied, setCopied] = useState(false);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    async function loadConversations() {
      const convs = await apiClient.getConversations(filter);
      setConversations(convs);
      if (convs.length > 0 && !activeConv) {
        setActiveConv(convs[0]);
      }
    }
    loadConversations();
  }, [filter, activeConv]);

  useEffect(() => {
    async function loadMessages() {
      if (activeConv) {
        const msgs = await apiClient.getMessages(activeConv.id);
        setMessages(msgs);
      }
    }
    loadMessages();
  }, [activeConv]);

  const handleSend = async () => {
    if (!replyText.trim() || !activeConv) return;
    setIsSending(true);
    await apiClient.sendMessage(activeConv.id, replyText, activeConv.account_id);
    const msgs = await apiClient.getMessages(activeConv.id);
    setMessages(msgs);
    setReplyText("");
    setIsSending(false);
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <AppShell>
      <div className="mb-4">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          Unified Inbox
        </h1>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Manage conversations across all 4 Instagram and WhatsApp accounts in one place.
        </p>
      </div>

      {/* Main Inbox Shell */}
      <div className="h-[calc(100vh-12rem)] min-h-[500px] glass-card rounded-mac-lg overflow-hidden flex flex-col md:flex-row border border-black/5 dark:border-white/5">
        {/* Left Column: Thread List */}
        <div className="w-full md:w-80 border-r border-black/5 dark:border-white/5 flex flex-col bg-white/40 dark:bg-[#12151E]/40">
          {/* Filter Tabs */}
          <div className="p-3 border-b border-black/5 dark:border-white/5 flex gap-1 bg-gray-100/50 dark:bg-gray-900/50">
            {(["all", "instagram", "whatsapp"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setFilter(tab)}
                className={cn(
                  "flex-1 py-1 px-2.5 rounded-lg text-xs font-semibold capitalize transition-all",
                  filter === tab
                    ? "bg-white dark:bg-gray-800 text-brand-600 dark:text-brand-400 shadow-xs"
                    : "text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
                )}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Conversation Items */}
          <div className="flex-1 overflow-y-auto divide-y divide-black/5 dark:divide-white/5">
            {conversations.map((c) => {
              const isSelected = activeConv?.id === c.id;
              const isWA = c.account_id.includes("wa");

              return (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setActiveConv(c)}
                  className={cn(
                    "w-full p-3.5 text-left flex items-start gap-3 transition-colors",
                    isSelected
                      ? "bg-brand-50/70 dark:bg-brand-500/10 border-l-4 border-brand-500"
                      : "hover:bg-black/5 dark:hover:bg-white/5"
                  )}
                >
                  <div
                    className={cn(
                      "w-9 h-9 rounded-xl flex items-center justify-center text-white font-bold text-xs shrink-0",
                      isWA ? "bg-emerald-600" : "bg-gradient-to-tr from-pink-500 to-purple-600"
                    )}
                  >
                    {c.contact.display_name.slice(0, 1)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-gray-900 dark:text-white truncate">
                        {c.contact.display_name}
                      </span>
                      <span className="text-[10px] text-gray-400">
                        {formatTimeAgo(c.updated_at)}
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-500 dark:text-gray-400 truncate mt-0.5">
                      {c.last_message_preview}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Column: Chat Viewer */}
        <div className="flex-1 flex flex-col bg-white/20 dark:bg-black/20">
          {activeConv ? (
            <>
              {/* Chat Header */}
              <div className="p-3.5 border-b border-black/5 dark:border-white/5 flex items-center justify-between bg-white/50 dark:bg-[#12151E]/50">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-800 flex items-center justify-center text-gray-600 dark:text-gray-300 font-bold text-xs">
                    {activeConv.contact.display_name[0]}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900 dark:text-white">
                      {activeConv.contact.display_name}
                    </div>
                    <div className="text-[10px] text-gray-400">
                      {activeConv.account_id.includes("wa") ? "WhatsApp" : "Instagram"} ·{" "}
                      {activeConv.account_id.includes("business") ? "Business" : "Personal"}
                    </div>
                  </div>
                </div>

                <div className="text-[10px] text-emerald-600 font-semibold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-500/20">
                  AI Assistant Active
                </div>
              </div>

              {/* Message History */}
              <div className="flex-1 p-4 overflow-y-auto space-y-3">
                {messages.map((m) => {
                  const isInbound = m.direction === "inbound";

                  return (
                    <div
                      key={m.id}
                      className={cn("flex flex-col", isInbound ? "items-start" : "items-end")}
                    >
                      <div
                        className={cn(
                          "max-w-[80%] rounded-2xl p-3 text-xs leading-relaxed shadow-xs relative group",
                          isInbound
                            ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-black/5 dark:border-white/5"
                            : "bg-brand-600 text-white"
                        )}
                      >
                        {m.content}

                        {/* Copy button for manual workflow */}
                        <button
                          type="button"
                          onClick={() => handleCopy(m.content)}
                          className="opacity-0 group-hover:opacity-100 absolute -bottom-5 right-1 px-1.5 py-0.5 rounded text-[10px] bg-black/70 text-white flex items-center gap-1 transition-opacity shadow-xs"
                          title="Copy text to clipboard"
                        >
                          {copied ? <Check className="w-2.5 h-2.5 text-emerald-400" /> : <Copy className="w-2.5 h-2.5" />}
                          <span>{copied ? "Copied" : "Copy"}</span>
                        </button>
                      </div>

                      <div className="flex items-center gap-1.5 mt-1 text-[10px] text-gray-400 px-1">
                        <span>{formatTimeAgo(m.created_at)}</span>
                        {m.is_ai_generated && (
                          <span className="flex items-center gap-0.5 text-brand-600 dark:text-brand-400">
                            <Sparkles className="w-2.5 h-2.5" /> AI Drafted
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Bottom Reply Box */}
              <div className="p-3 border-t border-black/5 dark:border-white/5 bg-white/50 dark:bg-[#12151E]/50">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    placeholder="Type a manual reply or edit the suggested text..."
                    className="flex-1 px-3.5 py-2 rounded-xl text-xs bg-white dark:bg-gray-900 border border-black/5 dark:border-white/10 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                  <button
                    type="button"
                    onClick={handleSend}
                    disabled={isSending || !replyText.trim()}
                    className="p-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white transition-all disabled:opacity-50"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-xs text-gray-400">
              Select a conversation to inspect messages
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
