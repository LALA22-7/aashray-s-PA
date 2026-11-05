# Aashray'sPA — Production Deployment Guide & Operations Runbook

## 1. System Architecture Overview

```
                                  INTERNET
                                      │
                   ┌──────────────────┼──────────────────┐
                   │                  │                  │
                   ▼                  ▼                  ▼
             Meta Platform       Frontend App       Account Owner
         (WhatsApp & Instagram)  (Next.js on Vercel) (Web Dashboard)
                   │                  │                  │
                   │ Webhooks         │ HTTPS API        │ Manual Copy / Controls
                   ▼                  ▼                  ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                 Render Web Service (Docker)                 │
       │                   FastAPI / Python 3.12                     │
       │                                                             │
       │   ├── Modular Monolith API (/api/v1/...)                    │
       │   ├── AI Orchestrator (Google Gemini API)                   │
       │   ├── Policy Engine & Emergency Stop                        │
       │   └── Channel Adapters (WhatsApp & Instagram)               │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
                       Managed PostgreSQL 16
                   (Supabase / Render Managed DB)
```

---

## 2. Secrets & Keys Generation Checklist

Run these commands locally before configuring your production environment:

```bash
# 1. Generate 32-byte Fernet key for database credential encryption:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Generate strong random secret keys for application and JWT tokens:
openssl rand -hex 32
openssl rand -hex 32

# 3. Choose high-entropy verify tokens for Meta Webhooks:
openssl rand -hex 16
```

---

## 3. Database Provisioning (Supabase or Render PostgreSQL)

### Option A: Supabase PostgreSQL (Recommended)
1. Go to [supabase.com](https://supabase.com) and create a new project.
2. In **Project Settings** $\rightarrow$ **Database**, locate the **Connection String** (Transaction pooler on port 5432 or 6543).
3. Ensure the connection URI is in standard format:
   ```text
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
4. Set `DATABASE_URL` in your production environment variables to this URI.

### Option B: Render Managed Database
If deploying via `render.yaml`, Render automatically provisions a managed PostgreSQL instance and binds `DATABASE_URL` directly to the web service.

---

## 4. Backend Deployment to Render

### Method 1: Infrastructure-as-Code via Blueprint (Fastest)
1. Push your repository to GitHub or GitLab.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** $\rightarrow$ **Blueprint**.
4. Select your `aashrays-pa` repository.
5. Render detects [`render.yaml`](../render.yaml) and provisions:
   - PostgreSQL Database (`aashrays-pa-db`)
   - Web Service (`aashrays-pa-backend`)
6. Enter the missing secret variables (`GEMINI_API_KEY`, `ENCRYPTION_KEY`, `CORS_ORIGINS`).
7. Click **Apply**.

### Method 2: Manual Web Service Setup
1. Click **New +** $\rightarrow$ **Web Service**.
2. Select your repository.
3. Configure settings:
   - **Environment**: Docker
   - **Docker Context**: `backend`
   - **DockerfilePath**: `backend/Dockerfile`
   - **Plan**: Starter ($7/mo)
   - **Health Check Path**: `/api/health`
4. Add environment variables according to [`.env.production.example`](../.env.production.example).
5. Click **Deploy Web Service**.

---

## 5. Meta Webhook Configuration Runbook

### A. WhatsApp Cloud API Webhook
1. Navigate to the **Meta App Dashboard** $\rightarrow$ **WhatsApp** $\rightarrow$ **Configuration**.
2. Under **Webhook**, click **Edit**:
   - **Callback URL**: `https://<your-render-backend-url>/webhooks/whatsapp`
   - **Verify Token**: Must match `WHATSAPP_VERIFY_TOKEN`.
3. Click **Verify and Save**. Meta will perform the handshake via `GET /webhooks/whatsapp`.
4. Under **Webhook Fields**, click **Manage** and subscribe to:
   - `messages`
5. Test by sending a WhatsApp message to your registered Business number.

### B. Instagram Messaging API Webhook
1. In Meta App Dashboard, navigate to **Messenger API for Instagram** $\rightarrow$ **Webhooks**.
2. Set:
   - **Callback URL**: `https://<your-render-backend-url>/webhooks/instagram`
   - **Verify Token**: Must match `INSTAGRAM_VERIFY_TOKEN`.
3. Subscribe to:
   - `messages`
   - `messaging_postbacks`
   - `message_deliveries`
   - `message_reads`
4. Confirm in the Meta testing tool that events respond with `200 OK`.

---

## 6. Database Migrations & Rollback Runbook

Alembic migrations are executed automatically during container startup via `entrypoint.sh`.

### Manual Migration Check via Render Shell
```bash
# SSH / Shell into Render container:
alembic current
alembic history

# Upgrade to latest revision:
alembic upgrade head

# Rollback one migration if needed:
alembic downgrade -1
```

---

## 7. Operational Playbook & Emergency Procedures

### Emergency Scenario: AI Malfunction or Message Looping
If the AI engine generates inappropriate responses or an external webhook loops:

1. **Immediate Global Emergency Stop**:
   Send a POST request to disable all outbound automation instantly:
   ```bash
   curl -X POST https://<your-backend-url>/api/automation/emergency-stop
   ```
   *Effect*: All automated outbound message dispatches across all accounts are terminated immediately. Responses are held as drafts for human review.

2. **Pause Automation Temporarily**:
   ```bash
   curl -X POST https://<your-backend-url>/api/automation/pause
   ```

3. **Per-Account Killswitch**:
   ```bash
   curl -X PATCH https://<your-backend-url>/api/accounts/<account-id>/automation \
     -H "Content-Type: application/json" \
     -d '{"automation_status": "disabled", "automation_mode": "manual"}'
   ```

4. **Resume Safe Operation**:
   ```bash
   curl -X POST https://<your-backend-url>/api/automation/resume
   ```

