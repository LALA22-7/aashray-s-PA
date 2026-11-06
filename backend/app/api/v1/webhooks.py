"""
Webhook endpoints for WhatsApp Cloud API and Instagram Messaging API.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.integrations.instagram.adapter import InstagramAdapter
from app.integrations.instagram.webhook import process_instagram_webhook
from app.integrations.whatsapp.adapter import WhatsAppAdapter
from app.integrations.whatsapp.personal_adapter import PersonalWhatsAppAdapter
from app.integrations.whatsapp.personal_webhook import process_personal_whatsapp_webhook
from app.integrations.whatsapp.webhook import process_whatsapp_webhook

router = APIRouter(prefix="/webhooks", tags=["Platform Webhooks"])


@router.get("/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
) -> Response:
    """
    Meta Webhook Verification Handshake for WhatsApp Cloud API.
    Returns the challenge string as raw plaintext if verify_token matches.
    """
    adapter = WhatsAppAdapter()
    challenge = adapter.verify_webhook_token(
        mode=hub_mode, token=hub_verify_token, challenge=hub_challenge
    )
    if challenge:
        return Response(content=challenge, media_type="text/plain", status_code=status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Webhook verification failed: Invalid verify token or mode.",
    )


@router.post("/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Process incoming WhatsApp Cloud API events (messages, status updates).
    Validates HMAC-SHA256 signature and returns 200 OK immediately to Meta.
    """
    raw_body = await request.body()
    adapter = WhatsAppAdapter()

    # Validate HMAC signature if app secret configured
    if not adapter.verify_signature(raw_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook HMAC signature.",
        )

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    result = process_whatsapp_webhook(payload_dict=payload, db=db, adapter=adapter)
    return result


# ── Meta Instagram Messaging API Endpoints ─────────────────────────


@router.get("/instagram")
def verify_instagram_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
) -> Response:
    """
    Meta Webhook Verification Handshake for Instagram Messaging API.
    Returns the challenge string as raw plaintext if verify_token matches.
    """
    adapter = InstagramAdapter()
    challenge = adapter.verify_webhook_token(
        mode=hub_mode, token=hub_verify_token, challenge=hub_challenge
    )
    if challenge:
        return Response(content=challenge, media_type="text/plain", status_code=status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Webhook verification failed: Invalid verify token or mode.",
    )


@router.post("/instagram")
async def receive_instagram_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Process incoming Instagram Messaging API events (messages, read receipts).
    Validates HMAC-SHA256 signature and returns 200 OK immediately to Meta.
    """
    raw_body = await request.body()
    adapter = InstagramAdapter()

    # Validate HMAC signature if app secret configured
    if not adapter.verify_signature(raw_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook HMAC signature.",
        )

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    result = process_instagram_webhook(payload_dict=payload, db=db, adapter=adapter)
    return result


# ── Personal WhatsApp Companion Bridge Endpoints ───────────────────


@router.post("/whatsapp-personal")
async def receive_personal_whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Process incoming personal WhatsApp events forwarded by the Baileys companion bridge.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload.")

    adapter = PersonalWhatsAppAdapter()
    result = process_personal_whatsapp_webhook(payload=payload, db=db, adapter=adapter)
    return result


@router.get("/whatsapp-personal/status")
def get_personal_whatsapp_bridge_status() -> dict:
    """
    Check companion device connection status (connected, qr_ready, disconnected).
    """
    adapter = PersonalWhatsAppAdapter()
    return adapter.get_status()


@router.get("/whatsapp-personal/qr")
def get_personal_whatsapp_qr() -> dict:
    """
    Fetch live QR code data URL for scanning with WhatsApp on personal phone.
    """
    adapter = PersonalWhatsAppAdapter()
    return adapter.get_qr()



