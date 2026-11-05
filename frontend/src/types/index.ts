export type PlatformType = "whatsapp" | "instagram";
export type AccountType = "personal" | "business";
export type AutomationMode = "disabled" | "approval" | "automatic";
export type AutomationStatus = "active" | "paused" | "disabled" | "error";

export interface PersonalityConfiguration {
  system_prompt_override?: string;
  tone?: string;
  formality_level?: number;
  emoji_usage?: number;
  hinglish_preference?: number;
  auto_reply_rules?: Record<string, boolean>;
}

export interface SocialAccount {
  id: string;
  platform: PlatformType;
  account_type: AccountType;
  display_name: string;
  platform_account_id?: string;
  integration_status: "connected" | "disconnected" | "error" | "pending";
  automation_mode: AutomationMode;
  automation_status: AutomationStatus;
  messages_handled: number;
  pending_approvals: number;
  last_sync_at?: string;
  personality?: PersonalityConfiguration;
}

export interface Contact {
  id: string;
  platform_contact_id: string;
  display_name: string;
  phone_number?: string;
  avatar_url?: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  account_id: string;
  direction: "inbound" | "outbound";
  content: string;
  sender_type: "contact" | "assistant" | "owner";
  delivery_status: "pending" | "sent" | "delivered" | "read" | "failed" | "received";
  is_ai_generated: boolean;
  owner_approved: boolean;
  created_at: string;
  ai_metadata?: {
    intent?: string;
    mode?: string;
    confidence?: number;
    requires_human?: boolean;
    reason?: string;
    policy_action?: string;
    policy_reason?: string;
  };
}

export interface Conversation {
  id: string;
  account_id: string;
  contact_id: string;
  contact: Contact;
  last_message_preview?: string;
  message_count: number;
  unread_count: number;
  status: "open" | "archived" | "escalated";
  created_at: string;
  updated_at: string;
}

export interface Approval {
  id: string;
  conversation_id: string;
  account_id: string;
  account_name: string;
  platform: PlatformType;
  account_type: AccountType;
  customer_name: string;
  incoming_message: string;
  proposed_reply: string;
  intent: string;
  confidence: number;
  status: "pending" | "approved" | "rejected" | "modified";
  created_at: string;
  reason?: string;
}

export interface Assistant {
  id: string;
  account_id: string;
  account_name: string;
  platform: PlatformType;
  account_type: AccountType;
  personality_summary: string;
  tone: string;
  hinglish_preference: number;
  emoji_usage: number;
  formality_level: number;
  autonomy_mode: AutomationMode;
  system_instruction: string;
  active: boolean;
  messages_processed: number;
}

export interface Lead {
  id: string;
  account_id: string;
  conversation_id: string;
  customer_name: string;
  enquiry: string;
  estimated_quantity?: number;
  location?: string;
  status: "new" | "contacted" | "qualified" | "converted" | "dropped";
  created_at: string;
}

export interface MetricSummary {
  connected_accounts: number;
  messages_received: number;
  messages_handled: number;
  pending_approvals: number;
  auto_reply_rate: number;
}

export interface RecentActivityItem {
  id: string;
  account_id: string;
  account_name: string;
  platform: PlatformType;
  account_type: AccountType;
  event_type: "inbound" | "auto_reply" | "pending_approval" | "approved" | "rejected" | "escalated";
  description: string;
  snippet?: string;
  timestamp: string;
  status: "live" | "pending" | "success" | "warning";
}

export interface BusinessKnowledgeItem {
  id: string;
  category: string;
  title: string;
  content: string;
  confidence_score: number;
  source: string;
  is_verified: boolean;
}
