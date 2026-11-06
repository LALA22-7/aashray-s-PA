import {
  Approval,
  Assistant,
  BusinessKnowledgeItem,
  Conversation,
  Message,
  MetricSummary,
  RecentActivityItem,
  SocialAccount,
} from "@/types";
import {
  MOCK_ACCOUNTS,
  MOCK_APPROVALS,
  MOCK_ASSISTANTS,
  MOCK_CONVERSATIONS,
  MOCK_KNOWLEDGE,
  MOCK_MESSAGES,
  MOCK_METRICS,
  MOCK_RECENT_ACTIVITY,
} from "./mock-data";

// Local fallback state
let localAccounts = [...MOCK_ACCOUNTS];
let localApprovals = [...MOCK_APPROVALS];
let localAssistants = [...MOCK_ASSISTANTS];
let localConversations = [...MOCK_CONVERSATIONS];
let localMessages = { ...MOCK_MESSAGES };
let localRecentActivity = [...MOCK_RECENT_ACTIVITY];
let localMetrics = { ...MOCK_METRICS };
let localKnowledge = [...MOCK_KNOWLEDGE];

export const apiClient = {
  // ── Metrics & Dashboard ──────────────────────────────────────
  async getMetrics(): Promise<MetricSummary> {
    try {
      const res = await fetch("/api/backend/metrics", { cache: "no-store" });
      if (res.ok) {
        const live = await res.json();
        return live;
      }
    } catch {
      // Fallback to local data
    }
    return {
      ...localMetrics,
      pending_approvals: localApprovals.filter((a) => a.status === "pending").length,
    };
  },

  async getRecentActivity(): Promise<RecentActivityItem[]> {
    try {
      const res = await fetch("/api/backend/recent-activity", { cache: "no-store" });
      if (res.ok) {
        const live = await res.json();
        if (live && live.length > 0) return live;
      }
    } catch {
      // Fallback
    }
    return localRecentActivity;
  },

  // ── Accounts ─────────────────────────────────────────────────
  async getAccounts(): Promise<SocialAccount[]> {
    try {
      const res = await fetch("/api/backend/accounts", { cache: "no-store" });
      if (res.ok) {
        const liveAccounts = await res.json();
        if (liveAccounts && liveAccounts.length > 0) {
          return liveAccounts.map((la: any) => ({
            id: la.id,
            platform: la.platform,
            account_type: la.account_type,
            display_name: la.display_name,
            platform_account_id:
              la.phone_number ||
              la.platform_account_id ||
              (la.platform === "whatsapp"
                ? la.account_type === "personal"
                  ? "+91-PERSONAL"
                  : "+91-BUSINESS"
                : la.account_type === "personal"
                ? "@handle"
                : "@aashrayspa"),
            integration_status: la.integration_status,
            automation_mode: la.automation_mode,
            automation_status: la.automation_status,
            messages_handled: la.automation_enabled ? 12 : 0,
            pending_approvals: 0,
            last_sync_at: la.last_sync_at || new Date().toISOString(),
            personality: la.personality,
          }));
        }
      }
    } catch {
      // Fallback
    }
    return localAccounts;
  },

  async updateAccountAutomation(
    accountId: string,
    mode: "disabled" | "approval" | "automatic"
  ): Promise<SocialAccount> {
    try {
      const res = await fetch(`/api/backend/accounts/${accountId}/automation`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ automation_mode: mode }),
      });
      if (res.ok) {
        const data = await res.json();
        return data;
      }
    } catch {
      // Fallback
    }
    localAccounts = localAccounts.map((acc) =>
      acc.id === accountId ? { ...acc, automation_mode: mode } : acc
    );
    return localAccounts.find((a) => a.id === accountId)!;
  },

  // ── Approvals ────────────────────────────────────────────────
  async getApprovals(): Promise<Approval[]> {
    try {
      const res = await fetch("/api/backend/approvals", { cache: "no-store" });
      if (res.ok) {
        const live = await res.json();
        if (live && live.length > 0) return live;
      }
    } catch {
      // Fallback
    }
    return localApprovals.filter((a) => a.status === "pending");
  },

  async approveMessage(approvalId: string): Promise<boolean> {
    try {
      const res = await fetch(`/api/backend/approvals/${approvalId}/approve`, {
        method: "POST",
      });
      if (res.ok) return true;
    } catch {
      // Fallback
    }
    localApprovals = localApprovals.map((a) =>
      a.id === approvalId ? { ...a, status: "approved" as const } : a
    );
    return true;
  },

  async rejectMessage(approvalId: string): Promise<boolean> {
    try {
      const res = await fetch(`/api/backend/approvals/${approvalId}/reject`, {
        method: "POST",
      });
      if (res.ok) return true;
    } catch {
      // Fallback
    }
    localApprovals = localApprovals.map((a) =>
      a.id === approvalId ? { ...a, status: "rejected" as const } : a
    );
    return true;
  },

  async editProposedReply(approvalId: string, updatedReply: string): Promise<boolean> {
    localApprovals = localApprovals.map((a) =>
      a.id === approvalId
        ? { ...a, proposed_reply: updatedReply, status: "modified" as const }
        : a
    );
    return true;
  },

  // ── AI Assistants ────────────────────────────────────────────
  async getAssistants(): Promise<Assistant[]> {
    try {
      const res = await fetch("/api/backend/accounts", { cache: "no-store" });
      if (res.ok) {
        const accs = await res.json();
        if (accs && accs.length > 0) {
          return accs.map((a: any) => ({
            id: `ast_${a.id}`,
            account_id: a.id,
            account_name: a.display_name,
            platform: a.platform,
            account_type: a.account_type,
            personality_summary:
              a.personality?.system_prompt_override?.slice(0, 70) ||
              (a.account_type === "personal"
                ? "Friendly, personal, and casual communication."
                : "Professional, structured brand representation."),
            tone: a.personality?.tone || (a.account_type === "personal" ? "Warm & Casual" : "Professional"),
            hinglish_preference: a.personality?.hinglish_preference ?? 50,
            emoji_usage: a.personality?.emoji_usage ?? (a.account_type === "personal" ? 70 : 25),
            formality_level: a.personality?.formality_level ?? (a.account_type === "personal" ? 20 : 80),
            autonomy_mode: a.automation_mode,
            system_instruction:
              a.personality?.system_prompt_override ||
              (a.account_type === "personal"
                ? "Act as Ashray's personal social media assistant. Sound natural and friendly."
                : "Act as Ashray's official brand representative. Be precise, polite, and helpful."),
            active: a.automation_enabled,
            messages_processed: 0,
          }));
        }
      }
    } catch {
      // Fallback
    }
    return localAssistants;
  },

  async updateAssistant(
    assistantId: string,
    updates: Partial<Assistant>
  ): Promise<Assistant> {
    try {
      const accountId = assistantId.replace("ast_", "");
      if (updates.system_instruction || updates.tone) {
        await fetch(`/api/backend/accounts/${accountId}/personality`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            system_prompt_override: updates.system_instruction,
            tone: updates.tone,
            formality_level: updates.formality_level,
            emoji_usage: updates.emoji_usage,
            hinglish_preference: updates.hinglish_preference,
          }),
        });
      }
      if (updates.autonomy_mode) {
        await fetch(`/api/backend/accounts/${accountId}/automation`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            automation_mode: updates.autonomy_mode,
          }),
        });
      }
    } catch {
      // Fallback
    }

    localAssistants = localAssistants.map((ast) =>
      ast.id === assistantId ? { ...ast, ...updates } : ast
    );
    return localAssistants.find((a) => a.id === assistantId)!;
  },

  // ── Inbox & Conversations ────────────────────────────────────
  async getConversations(platformFilter?: string): Promise<Conversation[]> {
    try {
      const res = await fetch("/api/backend/conversations", { cache: "no-store" });
      if (res.ok) {
        const liveConvs = await res.json();
        if (liveConvs && liveConvs.length > 0) {
          const mapped: Conversation[] = liveConvs.map((c: any) => ({
            id: c.id,
            account_id: c.account_id,
            contact_id: c.contact_id,
            contact: {
              id: c.contact_id,
              platform_contact_id: c.contact?.platform_contact_id || c.contact_id,
              display_name: c.contact?.display_name || "Contact",
              phone_number: c.contact?.phone_number,
            },
            last_message_preview: c.summary || "Conversation active",
            message_count: c.message_count || 1,
            unread_count: 0,
            status: c.status === "escalated" ? "escalated" : "open",
            created_at: c.created_at,
            updated_at: c.updated_at || c.created_at,
          }));

          if (!platformFilter || platformFilter === "all") return mapped;
          return mapped.filter((c) =>
            platformFilter === "whatsapp"
              ? c.account_id.includes("wa") || c.account_id.includes("whatsapp")
              : c.account_id.includes("ig") || c.account_id.includes("instagram")
          );
        }
      }
    } catch {
      // Fallback
    }

    if (!platformFilter || platformFilter === "all") {
      return localConversations;
    }
    return localConversations.filter((c) =>
      platformFilter === "whatsapp"
        ? c.account_id.includes("wa")
        : c.account_id.includes("ig")
    );
  },

  async getMessages(conversationId: string): Promise<Message[]> {
    try {
      const res = await fetch(`/api/backend/conversations/${conversationId}/messages`, {
        cache: "no-store",
      });
      if (res.ok) {
        const live = await res.json();
        if (live && live.length > 0) {
          return live.map((m: any) => ({
            id: m.id,
            conversation_id: m.conversation_id,
            account_id: m.account_id,
            direction: m.direction,
            content: m.content,
            sender_type: m.sender_type,
            delivery_status: m.delivery_status || "sent",
            is_ai_generated: m.is_ai_generated || false,
            owner_approved: m.owner_approved !== false,
            created_at: m.created_at,
            ai_metadata: m.ai_metadata,
          }));
        }
      }
    } catch {
      // Fallback
    }
    return localMessages[conversationId] || [];
  },

  async sendMessage(
    conversationId: string,
    content: string,
    accountId: string
  ): Promise<Message> {
    try {
      const res = await fetch(`/api/backend/conversations/${conversationId}/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          account_id: accountId,
          user_message: content,
          sender_type: "owner",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        return {
          id: data.id || `msg_${Date.now()}`,
          conversation_id: conversationId,
          account_id: accountId,
          direction: "outbound",
          content,
          sender_type: "owner",
          delivery_status: "sent",
          is_ai_generated: false,
          owner_approved: true,
          created_at: new Date().toISOString(),
        };
      }
    } catch {
      // Fallback
    }

    const newMsg: Message = {
      id: `msg_${Date.now()}`,
      conversation_id: conversationId,
      account_id: accountId,
      direction: "outbound",
      content,
      sender_type: "owner",
      delivery_status: "sent",
      is_ai_generated: false,
      owner_approved: true,
      created_at: new Date().toISOString(),
    };

    if (!localMessages[conversationId]) {
      localMessages[conversationId] = [];
    }
    localMessages[conversationId].push(newMsg);
    return newMsg;
  },

  // ── Emergency Controls ───────────────────────────────────────
  async triggerEmergencyStop(): Promise<{ status: string }> {
    try {
      const res = await fetch("/api/backend/automation/emergency-stop", {
        method: "POST",
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    localAccounts = localAccounts.map((a) => ({
      ...a,
      automation_mode: "disabled" as const,
      automation_status: "paused" as const,
    }));
    return { status: "emergency_stop_activated" };
  },

  async resumeAutomation(): Promise<{ status: string }> {
    try {
      const res = await fetch("/api/backend/automation/resume", {
        method: "POST",
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    localAccounts = localAccounts.map((a) => ({
      ...a,
      automation_status: "active" as const,
    }));
    return { status: "automation_resumed" };
  },

  // ── Knowledge Base ───────────────────────────────────────────
  async getKnowledge(): Promise<BusinessKnowledgeItem[]> {
    try {
      const res = await fetch("/api/backend/knowledge", { cache: "no-store" });
      if (res.ok) {
        const live = await res.json();
        if (live && live.length > 0) return live;
      }
    } catch {
      // Fallback
    }
    return localKnowledge;
  },
};
