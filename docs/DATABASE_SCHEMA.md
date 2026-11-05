# Aashray'sPA — Database Schema Documentation

## 1. Entity Relationship Overview

The PostgreSQL database enforces relational isolation and tenant privacy using UUID primary keys and foreign key constraints:

```
┌───────────────────────┐         ┌───────────────────────────────┐
│       accounts        │ 1     1 │   personality_configurations  │
│───────────────────────│─────────│───────────────────────────────│
│ id (UUID, PK)         │         │ account_id (FK -> accounts)   │
│ platform              │         │ tone                          │
│ account_type          │         │ formality_level               │
│ display_name          │         │ hinglish_preference           │
│ platform_account_id   │         │ emoji_usage                   │
│ automation_mode       │         │ system_prompt_override        │
│ automation_status     │         └───────────────────────────────┘
│ credentials_ciphertext│
└──────────┬────────────┘
           │ 1
           │
           │ *
┌──────────▼────────────┐         ┌───────────────────────────────┐
│     conversations     │ 1     * │           messages            │
│───────────────────────│─────────│───────────────────────────────│
│ id (UUID, PK)         │         │ id (UUID, PK)                 │
│ account_id (FK)       │         │ conversation_id (FK)          │
│ contact_id (FK)       │         │ account_id (FK)               │
│ status                │         │ platform_message_id (UNIQUE)  │
│ last_message_at       │         │ direction (inbound|outbound)  │
└───────────────────────┘         │ content                       │
                                  │ sender_type                   │
                                  │ delivery_status               │
                                  │ is_ai_generated               │
                                  │ owner_approved                │
                                  │ ai_metadata (JSON)            │
                                  └───────────────────────────────┘

┌───────────────────────┐         ┌───────────────────────────────┐
│         leads         │         │       webhook_events          │
│───────────────────────│         │───────────────────────────────│
│ id (UUID, PK)         │         │ id (UUID, PK)                 │
│ account_id (FK)       │         │ platform (whatsapp|instagram) │
│ conversation_id (FK)  │         │ platform_event_id (UNIQUE)    │
│ contact_id (FK)       │         │ status (processed|skipped)    │
│ customer_name         │         │ raw_payload (JSON)            │
│ enquiry               │         └───────────────────────────────┘
│ status                │
└───────────────────────┘
```
