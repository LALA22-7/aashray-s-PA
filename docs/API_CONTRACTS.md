# Aashray'sPA — API Contracts & Integration Specification

## Base URL
- Local Backend: `http://localhost:8000/api`
- Next.js Proxy: `/api/backend/*`

---

## 1. Accounts API

### `GET /accounts`
- **Description**: Returns all configured social media accounts.
- **Response**: `200 OK`
```json
[
  {
    "id": "uuid-string",
    "platform": "whatsapp | instagram",
    "account_type": "personal | business",
    "display_name": "WhatsApp (Business)",
    "platform_account_id": "PHONE_ID_OR_IG_HANDLE",
    "integration_status": "connected | disconnected",
    "automation_mode": "automatic | approval | disabled",
    "automation_status": "active | paused"
  }
]
```

### `PATCH /accounts/{account_id}/automation`
- **Description**: Updates operating mode (automatic, approval, disabled).
- **Body**: `{"automation_mode": "approval"}`
- **Response**: `200 OK`

---

## 2. Conversations & Messaging API

### `GET /conversations`
- **Description**: Retrieves conversations with contacts.
- **Parameters**: `account_id` (optional), `limit` (default 20).
- **Response**: `200 OK`

### `POST /conversations/manual-input`
- **Description**: AI-assisted manual message processing workflow for personal accounts.
- **Body**:
```json
{
  "account_id": "uuid",
  "sender_contact_id": "friend_phone_or_handle",
  "message_content": "Are you coming tonight?",
  "record_in_history": true
}
```
- **Response**: `200 OK` with generated AI draft and conversation context.

---

## 3. Automation & Safety Controls

### `POST /automation/emergency-stop`
- **Description**: Instantly terminates all outbound automated dispatch across all channels.
- **Response**: `200 OK` `{"status": "emergency_stop_activated"}`

### `POST /automation/pause`
- **Description**: Temporarily pauses automation.
- **Response**: `200 OK` `{"status": "automation_paused"}`

### `POST /automation/resume`
- **Description**: Resumes configured automation.
- **Response**: `200 OK` `{"status": "automation_resumed"}`

---

## 4. Webhook Endpoints
- `GET /webhooks/whatsapp` (Meta Handshake)
- `POST /webhooks/whatsapp` (Inbound Messages & Status Updates)
- `GET /webhooks/instagram` (Meta Handshake)
- `POST /webhooks/instagram` (Inbound Messages & Read Receipts)
