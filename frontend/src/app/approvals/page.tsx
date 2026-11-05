"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { apiClient } from "@/lib/api";
import { Approval } from "@/types";
import { Check, CheckCircle2, Clock, Edit2, Sparkles, X } from "lucide-react";
import { cn, formatTimeAgo } from "@/lib/utils";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  useEffect(() => {
    async function loadApprovals() {
      const data = await apiClient.getApprovals();
      setApprovals(data);
    }
    loadApprovals();
  }, []);

  const handleApprove = async (id: string) => {
    await apiClient.approveMessage(id);
    setApprovals((prev) => prev.filter((a) => a.id !== id));
    setActionNotice("Message successfully approved and dispatched via platform API.");
    setTimeout(() => setActionNotice(null), 3000);
  };

  const handleReject = async (id: string) => {
    await apiClient.rejectMessage(id);
    setApprovals((prev) => prev.filter((a) => a.id !== id));
    setActionNotice("Draft response rejected. No message will be sent.");
    setTimeout(() => setActionNotice(null), 3000);
  };

  const handleSaveEdit = async (id: string) => {
    await apiClient.editProposedReply(id, editText);
    setApprovals((prev) =>
      prev.map((a) => (a.id === id ? { ...a, proposed_reply: editText } : a))
    );
    setEditingId(null);
  };

  return (
    <AppShell>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-2">
            <span>Approval Centre</span>
            <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30">
              {approvals.length} Pending
            </span>
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Review, edit, or reject AI-generated responses before they are delivered to customers.
          </p>
        </div>
      </div>

      {actionNotice && (
        <div className="mb-6 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs font-semibold flex items-center gap-2 animate-in fade-in-0 duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          <span>{actionNotice}</span>
        </div>
      )}

      {/* Approvals List */}
      <div className="space-y-4">
        {approvals.length > 0 ? (
          approvals.map((appr) => {
            const isWA = appr.platform === "whatsapp";
            const isEditing = editingId === appr.id;

            return (
              <div
                key={appr.id}
                className="glass-card rounded-mac-lg p-5 border border-black/5 dark:border-white/5 space-y-4 shadow-sm"
              >
                {/* Header: Platform badge & Customer info */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        "w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-bold",
                        isWA
                          ? "bg-emerald-600"
                          : "bg-gradient-to-tr from-pink-500 to-purple-600"
                      )}
                    >
                      {isWA ? "WA" : "IG"}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <span>{appr.account_name}</span>
                        <span className="text-[10px] text-gray-400 font-normal">
                          · {formatTimeAgo(appr.created_at)}
                        </span>
                      </div>
                      <div className="text-[11px] text-gray-500 dark:text-gray-400">
                        Sender: <strong className="font-semibold text-gray-800 dark:text-gray-200">{appr.customer_name}</strong>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                      {appr.intent.replace("_", " ")}
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400">
                      {Math.round(appr.confidence * 100)}% Match
                    </span>
                  </div>
                </div>

                {/* Inbound Message */}
                <div className="p-3.5 rounded-xl bg-gray-50 dark:bg-gray-900/60 border border-black/5 dark:border-white/5 text-xs">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                    Incoming Customer Message
                  </div>
                  <div className="text-gray-800 dark:text-gray-200 italic font-medium">
                    &ldquo;{appr.incoming_message}&rdquo;
                  </div>
                </div>

                {/* AI Proposed Reply */}
                <div className="p-3.5 rounded-xl bg-brand-50/50 dark:bg-brand-500/10 border border-brand-200/50 dark:border-brand-500/20 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      <span>Proposed AI Response</span>
                    </div>

                    {!isEditing && (
                      <button
                        type="button"
                        onClick={() => {
                          setEditingId(appr.id);
                          setEditText(appr.proposed_reply);
                        }}
                        className="text-[11px] font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
                      >
                        <Edit2 className="w-3 h-3" />
                        <span>Edit</span>
                      </button>
                    )}
                  </div>

                  {isEditing ? (
                    <div className="space-y-2 mt-2">
                      <textarea
                        rows={3}
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="w-full p-2.5 rounded-lg text-xs bg-white dark:bg-gray-900 border border-brand-400 text-gray-900 dark:text-white focus:outline-none"
                      />
                      <div className="flex gap-2 justify-end">
                        <button
                          type="button"
                          onClick={() => setEditingId(null)}
                          className="px-2.5 py-1 rounded-md text-[11px] font-semibold text-gray-600 dark:text-gray-400 hover:bg-black/5"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          onClick={() => handleSaveEdit(appr.id)}
                          className="px-3 py-1 rounded-md text-[11px] font-bold bg-brand-600 text-white hover:bg-brand-500"
                        >
                          Save Changes
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-gray-900 dark:text-white leading-relaxed">
                      {appr.proposed_reply}
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-end gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => handleReject(appr.id)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-600 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 transition-colors"
                  >
                    Reject
                  </button>

                  <button
                    type="button"
                    onClick={() => handleApprove(appr.id)}
                    className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Approve & Send</span>
                  </button>
                </div>
              </div>
            );
          })
        ) : (
          <div className="glass-card rounded-mac p-12 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto" />
            <div className="text-sm font-bold text-gray-900 dark:text-white">
              All caught up!
            </div>
            <div className="text-xs text-gray-400 max-w-sm mx-auto">
              There are no pending responses awaiting your approval. Outbound automation is running smoothly.
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
