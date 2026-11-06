/**
 * WhatsApp Multi-Device Companion Bridge for Aashray'sPA
 * Connects personal WhatsApp via QR code scan (Linked Devices)
 * and bridges incoming/outgoing events to the FastAPI backend.
 */

const express = require("express");
const cors = require("cors");
const QRCode = require("qrcode");
const pino = require("pino");
const path = require("path");
const fs = require("fs");

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} = require("@whiskeysockets/baileys");

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.BRIDGE_PORT || 3001;
const FASTAPI_WEBHOOK_URL =
  process.env.FASTAPI_WEBHOOK_URL ||
  "http://localhost:8000/webhooks/whatsapp-personal";

const AUTH_DIR = path.join(__dirname, "auth_info_baileys");
if (!fs.existsSync(AUTH_DIR)) {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
}

let sock = null;
let connectionStatus = "initializing"; // "qr_ready" | "connected" | "disconnected"
let rawQr = null;
let qrImageDataUrl = null;
let connectedPhone = null;

const logger = pino({ level: process.env.LOG_LEVEL || "silent" });

async function initBaileys() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    auth: state,
    logger,
    printQRInTerminal: true,
    browser: ["Aashray'sPA Command Centre", "Chrome", "1.0.0"],
    syncFullHistory: false,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      rawQr = qr;
      connectionStatus = "qr_ready";
      try {
        qrImageDataUrl = await QRCode.toDataURL(qr);
      } catch (err) {
        console.error("Error generating QR Data URL:", err);
      }
      console.log("📲 New WhatsApp QR Code generated. Ready to scan!");
    }

    if (connection === "close") {
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
      connectionStatus = "disconnected";
      rawQr = null;
      qrImageDataUrl = null;
      connectedPhone = null;

      console.log(
        `⚠️ WhatsApp bridge connection closed (status: ${statusCode}). Reconnecting: ${shouldReconnect}`
      );
      if (shouldReconnect) {
        setTimeout(initBaileys, 3000);
      }
    } else if (connection === "open") {
      connectionStatus = "connected";
      rawQr = null;
      qrImageDataUrl = null;
      const userJid = sock.user?.id || "";
      connectedPhone = userJid.split(":")[0] || userJid.split("@")[0];
      console.log(`✅ WhatsApp Personal linked successfully! Number: +${connectedPhone}`);
    }
  });

  // Forward incoming personal messages to FastAPI backend
  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;

    for (const msg of messages) {
      if (!msg.message) continue;

      const messageContent =
        msg.message.conversation ||
        msg.message.extendedTextMessage?.text ||
        msg.message.imageMessage?.caption ||
        "";

      if (!messageContent) continue;

      const remoteJid = msg.key.remoteJid || "";
      if (remoteJid.endsWith("@g.us")) {
        // Group messages: can optionally be handled or skipped for 1-to-1 chats
        continue;
      }

      const senderPhone = remoteJid.split("@")[0];
      const isFromMe = msg.key.fromMe || false;
      const senderName = msg.pushName || senderPhone;

      const payload = {
        event: "message",
        platform_message_id: msg.key.id,
        from: senderPhone,
        sender_name: senderName,
        text: messageContent,
        is_from_me: isFromMe,
        timestamp: Number(msg.messageTimestamp) || Math.floor(Date.now() / 1000),
      };

      try {
        const resp = await fetch(FASTAPI_WEBHOOK_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!resp.ok) {
          console.error(`FastAPI webhook returned ${resp.status}:`, await resp.text());
        }
      } catch (err) {
        console.error("Error forwarding message to FastAPI webhook:", err.message);
      }
    }
  });
}

// ── HTTP API for Dashboard & FastAPI Backend ─────────────────────

// Health and Status
app.get("/status", (req, res) => {
  res.json({
    status: connectionStatus,
    phone: connectedPhone,
    has_qr: !!qrImageDataUrl,
  });
});

// QR Code image / string for dashboard modal
app.get("/qr", (req, res) => {
  if (connectionStatus === "connected") {
    return res.json({
      status: "connected",
      message: "Device already linked.",
      phone: connectedPhone,
    });
  }

  if (!qrImageDataUrl) {
    return res.json({
      status: connectionStatus,
      message: "QR code generating... please retry in 2 seconds.",
    });
  }

  res.json({
    status: "qr_ready",
    raw_qr: rawQr,
    qr_image: qrImageDataUrl,
  });
});

// Outbound Message Dispatch
app.post("/send", async (req, res) => {
  const { to, text } = req.body;
  if (!to || !text) {
    return res.status(400).json({ error: "Missing 'to' or 'text' in payload." });
  }

  if (connectionStatus !== "connected" || !sock) {
    return res.status(503).json({
      error: "WhatsApp Personal companion bridge is not linked. Please scan QR first.",
    });
  }

  const cleanPhone = to.replace(/[^0-9]/g, "");
  const jid = `${cleanPhone}@s.whatsapp.net`;

  try {
    const sent = await sock.sendMessage(jid, { text });
    res.json({
      success: true,
      message_id: sent.key.id,
      to: cleanPhone,
    });
  } catch (err) {
    console.error("Error sending message via Baileys:", err);
    res.status(500).json({ error: err.message });
  }
});

// Disconnect / Log out
app.post("/logout", async (req, res) => {
  if (sock) {
    try {
      await sock.logout();
      fs.rmSync(AUTH_DIR, { recursive: true, force: true });
      connectionStatus = "disconnected";
      connectedPhone = null;
      setTimeout(initBaileys, 1000);
      return res.json({ success: true, message: "Logged out companion device." });
    } catch (err) {
      return res.status(500).json({ error: err.message });
    }
  }
  res.json({ success: true });
});

app.listen(PORT, () => {
  console.log(`🚀 Aashray'sPA WhatsApp Companion Bridge listening on port ${PORT}`);
  initBaileys().catch((err) => console.error("Error booting Baileys:", err));
});

