# WhatsApp Business App & Cloud API Coexistence Guide

## Executive Summary for Aashray'sPA
This document provides the technical requirements, limitations, and operational guidelines for integrating WhatsApp with **Aashray'sPA**.

---

## 1. The Two-Number Setup
Aashray operates with **two distinct physical phone numbers**:
1. **Personal Phone Number** (`+91-PERSONAL`):
   - Used for friends, family, and casual daily chats on standard personal WhatsApp.
   - **Integration Strategy**: AI-assisted manual workflow (`POST /api/conversations/manual-input`).
   - The owner copies incoming messages into the dashboard and receives context-aware, casual Hinglish reply drafts without risking phone number bans or violating Meta ToS.
2. **Business Phone Number** (`+91-BUSINESS`):
   - Dedicated exclusively to the Bottle Advertising Agency.
   - Used for customer inquiries, lead qualification, and campaign support.
   - **Integration Strategy**: Official Meta WhatsApp Cloud API with automated response capabilities.

---

## 2. WhatsApp Business App vs. Cloud API Coexistence
> [!WARNING]
> **Can the WhatsApp Business App and the Cloud API operate on the same phone number simultaneously?**
> **NO.** Meta strictly enforces a 1-to-1 relationship between a phone number and a WhatsApp client.

### What Happens During Migration?
- A phone number registered with the WhatsApp Business mobile app must be **deregistered / deleted** from the mobile app before it can be registered on Meta's Cloud API platform.
- Once registered with the Cloud API, the mobile WhatsApp Business app **will no longer connect or receive messages** for that number on your phone.
- All customer conversations and interactions must flow through your software interface (**Aashray'sPA Control Centre**).

### Recommended Action Plan
- Keep the Personal phone number on the standard mobile WhatsApp app (using manual AI assistance).
- For the Business phone number, once ready for full live automation, migrate the business number to Meta Cloud API and manage all business chats through the Aashray'sPA dashboard.

---

## 3. Meta Messaging Policies & Restrictions

### A. The 24-Hour Customer Service Window
- When a customer sends a message to the business number, a **24-hour service window** opens.
- Within this 24-hour window, the assistant can reply automatically with free-form text messages.
- Outside the 24-hour window, the business can **only** send pre-approved **Meta Message Templates** (opt-in required).

### B. Messaging Tiers & Rate Limits
- **Tier 1 (Unverified / New)**: 250 unique business-initiated conversations per 24 hours.
- **Tier 2 (Standard Verified)**: 1,000 conversations / 24 hours.
- **Tier 3 (Scaled)**: 10,000 conversations / 24 hours.
- *Customer-initiated conversations (replies)* are not restricted by conversation tier limits as long as the 24-hour window is respected.

---

## 4. Webhook Setup Checklist
1. Create a Meta Developer App under **Meta for Developers**.
2. Add the **WhatsApp** product.
3. Configure the Webhook:
   - **Callback URL**: `https://<YOUR_DOMAIN>/webhooks/whatsapp`
   - **Verify Token**: Must match `WHATSAPP_VERIFY_TOKEN` in `.env`.
   - **Subscribed Fields**: `messages`.
4. Copy the **Phone Number ID** and generate a permanent **System User Access Token** with `whatsapp_business_messaging` permission.
5. Save the credentials via the dashboard (`POST /api/accounts/{id}/connect`).

