# Instagram Integration & Messaging Architecture Guide

## Overview

Aashray'sPA maintains a strict separation between **Personal Instagram** and **Business Instagram**:

1. **Personal Instagram (Account 3)**:
   - Type: Personal Instagram Account.
   - Purpose: Social connections, family, friends, personal DMs, casual discussions.
   - Architecture: **Manual AI-Assisted Workflow** via the central dashboard (`POST /api/conversations/manual-input`).
   - Anti-Abuse & Policy: Zero scraping, zero unofficial automation, zero headless browser simulation. Full compliance with Meta Platform Terms.

2. **Business Instagram (Account 4)**:
   - Type: Professional Account (Instagram Business or Creator Account connected to a Facebook Page).
   - Purpose: Advertising inquiries, branded bottle campaigns, lead generation, customer support.
   - Architecture: **Official Meta Instagram Messaging API (Graph API v21.0)** with automatic reply dispatch, safety policy evaluation, and automated lead capture.

---

## Meta Instagram Messaging Architecture

```
                                  Meta Platform
                                       │
                         [Instagram Direct Message]
                                       │
                                       ▼
                     GET/POST /webhooks/instagram
                                       │
                         ┌─────────────┴─────────────┐
                         │   HMAC-SHA256 Signature   │
                         │   Token Verification      │
                         └─────────────┬─────────────┘
                                       │
                         ┌─────────────▼─────────────┐
                         │   Event Deduplication     │
                         │   (Skip if already seen)  │
                         └─────────────┬─────────────┘
                                       │
                         ┌─────────────▼─────────────┐
                         │   Resolve Account /       │
                         │   Contact / Conversation  │
                         └─────────────┬─────────────┘
                                       │
                         ┌─────────────▼─────────────┐
                         │   AI Response Generation  │
                         │   (Gemini + Persona +     │
                         │    Bottle Knowledge)      │
                         └─────────────┬─────────────┘
                                       │
                         ┌─────────────▼─────────────┐
                         │   Safety Policy Engine    │
                         └──────┬─────────────┬──────┘
                                │             │
                    AUTOMATIC   │             │  APPROVAL / ESCALATION
                                ▼             ▼
                     ┌──────────────────┐   ┌──────────────────┐
                     │ Outbound Dispatch│   │ Draft Saved for  │
                     │ (Graph API /me)  │   │ Human Review     │
                     └────────┬─────────┘   └──────────────────┘
                              │
                     ┌────────▼─────────┐
                     │ Lead Qualified & │
                     │ Stored in CRM    │
                     └──────────────────┘
```

---

## Meta Messaging Policies & Constraints

### 1. 24-Hour Standard Messaging Window
- Inbound messages from Instagram users open a standard **24-hour service window**.
- Within this 24-hour window, the assistant can reply with free-form conversational messages.
- Our adapter tracks message timestamps and validates:
  ```python
  InstagramAdapter.is_within_messaging_window(last_inbound_time)
  ```

### 2. Human-Agent Tag Extension (7-Day Window)
- Meta allows an extended **7-day window** for approved applications responding to complex customer support inquiries using the `HUMAN_AGENT` message tag.
- When human review or escalation is flagged in Aashray'sPA, replies can be sent outside the 24-hour window if configured with this tag.

### 3. Echo Messages
- Meta sends webhook events whenever any message is sent in the thread, including messages sent by the business account itself (`is_echo: true`).
- Aashray'sPA automatically skips echo messages to prevent infinite reply loops.

### 4. Prerequisite Checklist for Production Meta Onboarding
1. Convert Instagram account to an **Instagram Professional Account**.
2. Link the Instagram account to a **Facebook Page**.
3. Create a **Meta Developer App** with the `Instagram Graph API` and `Messenger API for Instagram` products added.
4. Request permissions:
   - `instagram_basic`
   - `instagram_manage_messages`
   - `pages_manage_metadata`
5. Configure the Webhook subscription URL: `https://<your-backend-domain>/webhooks/instagram`.
6. Set the `Verify Token` matching `INSTAGRAM_VERIFY_TOKEN`.
7. Subscribe to `messages`, `messaging_postbacks`, `message_deliveries`, and `message_reads`.
