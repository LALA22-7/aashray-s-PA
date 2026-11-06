# Aashray'sPA — Complete Setup, Integration & Hosting Master Manual

> **One AI Brain. Four Account Identities. Four Independent Personalities. One Control Dashboard.**

This document is your master operational blueprint. It walks you through running the entire system locally, linking all four social media accounts (including the **WhatsApp Personal Companion QR bridge** and **Instagram Creator mode**), deploying the stack to production cloud hosting (Render + Supabase + Vercel), and operating the daily command centre safely.

---

## 1. System Architecture Map

```
                                      INTERNET
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            │                             │                             │
            ▼                             ▼                             ▼
   Official Meta APIs             Companion Bridge               Account Owner
  (Business WA & IG)              (Personal WA QR)             (Ashray on Phone/PC)
            │                             │                             │
            │ Webhooks                    │ Webhooks                    │ Next.js UI
            ▼                             ▼                             ▼
  ┌───────────────────────────────────────────────────────────────────────────────┐
  │                           FastAPI Backend (:8000)                             │
  │                                                                               │
  │  ├── 4 Isolated Personas (Hinglish/Casual Personal vs Professional Bottle Ads)│
  │  ├── Safety Policy Engine (Emergency Stop, Approvals, Escalations)            │
  │  ├── Sliding-Window Conversation Memory & Verified Bottle Knowledge Base      │
  │  └── Channel Dispatchers (Meta Graph API & Personal Companion Bridge)         │
  └──────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
                            PostgreSQL 16 Database
                        (Supabase or Render PostgreSQL)
```

---

## 2. Local Quickstart (Running Everything in 3 Terminals)

### Terminal 1: FastAPI Backend
```powershell
cd "d:\PROJECTS\aashray's PA\backend"

# Activate Python virtual environment
.\.venv\Scripts\activate

# Run database migrations
alembic upgrade head

# Seed initial 4 accounts and verified bottle advertising knowledge
python -m scripts.seed_accounts

# Start the API server on port 8000
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

---

### Terminal 2: WhatsApp Personal Companion Bridge (Baileys)
```powershell
cd "d:\PROJECTS\aashray's PA\services\whatsapp-bridge"

# Start the companion bridge on port 3001
node server.js
```
- Bridge Status: `http://localhost:3001/status`
- Live QR Endpoint: `http://localhost:3001/qr`

---

### Terminal 3: Next.js Command Centre (Web Dashboard)
```powershell
cd "d:\PROJECTS\aashray's PA\frontend"

# Launch the Next.js development server on port 3000
npm run dev
```
Open **`http://localhost:3000`** in your browser.

- **Default Owner Username**: `ashray` (or `satyam`)
- **Default Owner Password**: Any password $\ge$ 6 characters (e.g. `ashray2026`)

---

## 3. Step-by-Step Account Integration Walkthrough

---

### Account 1: Personal WhatsApp (`+91-PERSONAL`)
*(Method: WhatsApp Multi-Device QR Code Companion Bridge)*

This connects your personal WhatsApp phone number so the AI can automatically read and reply to your friends/family while you **keep using your regular WhatsApp app on your physical phone**.

1. Start Terminal 2 (`services/whatsapp-bridge` running on port 3001).
2. Open the Dashboard at `http://localhost:3000/accounts`.
3. Locate the **WhatsApp (Personal)** card.
4. Click **Link Companion Device via QR Code**. A modal opens displaying the live QR code.
5. On your personal mobile phone:
   - Open **WhatsApp**.
   - Tap **Settings** (iPhone) or **three dots $\rightarrow$ Linked Devices** (Android).
   - Tap **Link a Device**.
   - Point your camera at the screen to scan the QR code.
6. The terminal prints: `✅ WhatsApp Personal linked successfully! Number: +91XXXXXXXXXX`.
7. **Test it**: Have a friend text your personal number: *"Bro are you free tonight?"*.
   - If Operating Mode is **Automatic**: Your personal number immediately replies back in natural Hinglish!
   - If Operating Mode is **Approval**: The message appears in your `/approvals` dashboard for you to review and click **Approve & Send**!
   - If you reply manually from your phone, it syncs two-way into the dashboard inbox.

---

### Account 2: Business WhatsApp (`+91-BUSINESS`)
*(Method: Official Meta WhatsApp Cloud API v21.0)*

This connects your dedicated agency business phone number for bottle advertising campaigns.

1. Go to [developers.facebook.com](https://developers.facebook.com) and log in with your Meta account.
2. Click **My Apps** $\rightarrow$ **Create App** $\rightarrow$ Select **Other** $\rightarrow$ Select **Business** as the app type.
3. In the App Dashboard, scroll to **Add products to your app** and click **Set up** under **WhatsApp**.
4. Meta provides:
   - **Phone Number ID**: Copy this to `WHATSAPP_BUSINESS_PHONE_ID`.
   - **Temporary Access Token** (or Permanent System User Token): Copy to `WHATSAPP_BUSINESS_ACCESS_TOKEN`.
5. In the left sidebar, click **WhatsApp** $\rightarrow$ **Configuration**:
   - Under **Webhook**, click **Edit**.
   - **Callback URL**: `https://<your-backend-domain>/webhooks/whatsapp`
   - **Verify Token**: Must match `WHATSAPP_VERIFY_TOKEN` (default: `aashrays_pa_wa_verify_token`).
   - Click **Verify and Save**. Meta will perform the handshake with our backend.
6. Under **Webhook Fields**, click **Manage** and subscribe to:
   - `messages`
7. Now when clients text your business number asking for bottle advertising quotes, the AI classifies the intent, accesses bottle package pricing, qualifies the lead, and sends the reply automatically!

---

### Account 3: Personal Instagram (`@your_personal_handle`)
*(Method: Creator Account via Meta Official Messaging API)*

To get 100% automated replies on your personal Instagram without getting your personal account shadowbanned or locked:

1. Open the **Instagram App** on your phone.
2. Go to your Profile $\rightarrow$ **Settings and Privacy** $\rightarrow$ **Account type and tools** $\rightarrow$ Tap **Switch to Professional Account**.
3. Select **Creator** (ideal for individuals/creators; it keeps your personal friends, reels, and aesthetic unchanged).
4. Under **Settings** $\rightarrow$ **Messages and story replies** $\rightarrow$ **Message controls**, turn ON **Allow Access to Messages** (this permits third-party API automation).
5. Link your Instagram account to a Facebook Page (you can create a simple private/unlisted page named "Ashray Personal").
6. In your Meta Developer App, add the **Messenger API for Instagram** product.
7. Configure the Webhook:
   - **Callback URL**: `https://<your-backend-domain>/webhooks/instagram`
   - **Verify Token**: Must match `INSTAGRAM_VERIFY_TOKEN`.
   - Subscribe to: `messages`.

---

### Account 4: Business Instagram (`@aashrayspa`)
*(Method: Professional Account via Meta Official Messaging API)*

1. In your Instagram agency account (`@aashrayspa`), make sure it is set to **Business Account**.
2. Link it to your official Agency Facebook Page in Meta Business Suite.
3. In your Meta Developer App:
   - Generate a Page Access Token with permissions:
     - `instagram_basic`
     - `instagram_manage_messages`
     - `pages_manage_metadata`
   - Set token in `INSTAGRAM_ACCESS_TOKEN`.
4. Webhook URL: `https://<your-backend-domain>/webhooks/instagram`.
5. Now all DMs to `@aashrayspa` regarding campaigns, pricing, or minimum order quantities receive automated, verified responses.

---

## 4. Production Cloud Deployment Walkthrough

---

### Step 1: Provision Managed PostgreSQL (Supabase)

1. Sign up / log in to [Supabase](https://supabase.com).
2. Click **New Project** $\rightarrow$ Name it `aashrays-pa-db` $\rightarrow$ Choose a strong database password.
3. Once provisioned, go to **Project Settings** $\rightarrow$ **Database**.
4. Under **Connection String**, choose **URI** (Mode: Transaction or Session pooler).
5. Copy the connection URI:
   ```text
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
6. This will be your production `DATABASE_URL`.

---

### Step 2: Generate Production Cryptographic Keys

Run this once in PowerShell to generate your production encryption and JWT keys:

```powershell
# 1. 32-byte Fernet key for database credential encryption:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Strong secret keys:
python -c "import secrets; print(secrets.token_hex(32))"
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### Step 3: Deploy Backend to Render

You can deploy using Render's Blueprint with [`render.yaml`](../render.yaml) or as a Web Service:

1. Push your repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com), click **New +** $\rightarrow$ **Blueprint**.
3. Select your `aashrays-pa` repository. Render automatically reads `render.yaml`.
4. Fill in the environment variables:
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string.
   - `ENCRYPTION_KEY`: The Fernet key generated in Step 2.
   - `SECRET_KEY`: Random 32+ character hex string.
   - `JWT_SECRET_KEY`: Random 32+ character hex string.
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `CORS_ORIGINS`: `["https://aashrays-pa.vercel.app"]`
   - `WHATSAPP_PERSONAL_BRIDGE_URL`: `https://your-whatsapp-bridge.onrender.com` (or local bridge URL).
5. Click **Apply**.
6. The backend boots, verifies production readiness, applies Alembic migrations automatically, and starts listening on HTTPS!

---

### Step 4: Deploy WhatsApp Companion Bridge to Render

1. In Render, click **New +** $\rightarrow$ **Web Service**.
2. Point to the repository $\rightarrow$ Set **Root Directory** to `services/whatsapp-bridge`.
3. Set **Runtime** to `Node`.
4. **Build Command**: `npm install`
5. **Start Command**: `node server.js`
6. Add environment variable:
   - `FASTAPI_WEBHOOK_URL`: `https://<your-render-backend-url>/webhooks/whatsapp-personal`
7. Click **Create Web Service**. Add a persistent disk (`/auth_info_baileys`) so the QR pairing session survives container restarts!

---

### Step 5: Deploy Frontend Command Centre to Vercel

1. Log in to [Vercel](https://vercel.com) $\rightarrow$ Click **Add New** $\rightarrow$ **Project**.
2. Select your repository.
3. In Project Settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
4. In **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: `https://<your-render-backend-url>`
5. Click **Deploy**.
6. Vercel builds and deploys your Next.js command centre in under 60 seconds with global CDN and HTTPS!

---

## 5. Daily Operations & Safety Playbook

### 1. Unified Inbox (`/inbox`)
- View all active conversations across all 4 accounts in real time.
- Filter by All, Instagram, or WhatsApp.
- If a personal account is in manual copilot mode, use the **1-Click Copy** button to instantly copy the AI draft and send it.

### 2. Approval Centre (`/approvals`)
- Any message flagged as sensitive, price negotiation, or from an account in **Approval Mode** is queued here.
- Actions:
  - **Approve & Send**: Dispatches message via the appropriate platform adapter.
  - **Edit Response**: Make inline tweaks to the copy, then send.
  - **Reject**: Deletes draft; no message will be delivered.

### 3. AI Assistants Editor (`/assistants`)
- Tune prompt instructions for each of the 4 personas individually.
- Adjust the **Hinglish Mixture** slider (from pure English to authentic street Hinglish).
- Adjust the **Emoji Usage** slider.
- Switch autonomy mode between **Automatic (Direct Send)** and **Approval Mode**.

### 4. Verified Bottle Advertising Knowledge Base (`/assistants`)
- Add or update pricing packages, minimum order quantities (MOQs), and delivery SLAs.
- The AI never hallucinates pricing—it answers strictly from verified entries in this knowledge base.

### 5. Immediate Emergency Stop Trigger
If an external bot loops, Meta sends erroneous webhooks, or you want to freeze all AI automation immediately:
- In the top-right header of the dashboard, click **Emergency Stop**.
- Or send an HTTP POST request:
  ```bash
  curl -X POST https://<your-backend-url>/api/automation/emergency-stop
  ```
- **Effect**: All automatic outbound messaging is terminated immediately across all accounts. Every subsequent message is held in the Approval Centre for manual review. Click **Resume Safe AI** to return to normal.

