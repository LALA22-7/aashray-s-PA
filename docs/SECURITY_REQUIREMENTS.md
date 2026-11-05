# Aashray'sPA — Security & Privacy Architecture

## 1. Single-Owner Protection Model
- No public user registration or signup routes exist.
- Hardware authentication / persistent owner sessions for Ashray.
- Direct object reference protection: all database queries verify ownership.

## 2. Platform Credential Encryption
- All Meta Access Tokens and App Secrets are encrypted using symmetric 32-byte Fernet AES-CBC keys (`ENCRYPTION_KEY`).
- Cleartext credentials never enter logs, client responses, or version control.

## 3. Webhook Authentication
- Meta calls require HMAC-SHA256 signature headers (`X-Hub-Signature-256`) computed with `WHATSAPP_APP_SECRET` and `INSTAGRAM_APP_SECRET`.
- Challenge handshakes require secret `verify_token` verification.

## 4. Prompt Injection Defense
- Incoming contact messages are isolated inside strict `<UNTRUSTED_CONTACT_INPUT>` delimiters before being submitted to the Gemini AI model.
- System instructions explicitly forbid the AI from evaluating instructions found inside untrusted user input blocks.
