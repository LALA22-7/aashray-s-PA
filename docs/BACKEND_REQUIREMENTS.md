# Aashray'sPA — Backend Requirements Specification

## 1. Executive Summary
This document outlines the architecture, service boundaries, and security enforcement models implemented in the FastAPI backend to support the **Aashray'sPA** Next.js command centre.

---

## 2. Core Functional Requirements

### 2.1 Single-Owner Identity & Authentication
- The backend serves a single tenant: Ashray.
- All protected API routes (`/api/accounts`, `/api/conversations`, `/api/leads`, `/api/knowledge`) enforce session verification.
- Tokens and secrets are never returned in client responses.

### 2.2 Four Independent Account Identifiers
The backend maintains strict multi-channel boundaries across:
1. `Instagram Personal` (Manual AI copy/paste assistant).
2. `Instagram Business` (Meta Instagram Messaging API v21.0).
3. `WhatsApp Personal` (Manual AI copy/paste assistant).
4. `WhatsApp Business` (Meta WhatsApp Cloud API v21.0).

No shared conversation memory or cross-account leakage is permitted.

### 2.3 Policy Enforcement & Safety Controls
- Automatic outbound messages are halted when:
  - Global emergency stop is active (`POST /api/automation/emergency-stop`).
  - Global pause is active (`POST /api/automation/pause`).
  - Account is in `approval` mode.
  - Inbound intent is flagged as `complaint`, `negotiation`, or `sensitive_conversation`.
  - Confidence score falls below 0.70.

### 2.4 Idempotency & Webhook Deduplication
- Meta incoming WAMIDs and MIDs are recorded in `webhook_events`.
- Replay attacks or duplicate deliveries are rejected immediately with 200 OK without generating duplicate outbound messages.
