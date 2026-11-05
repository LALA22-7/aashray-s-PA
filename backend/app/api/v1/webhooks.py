"""
Webhook endpoints for WhatsApp Cloud API and Instagram Messaging API.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.integrations.whatsapp.adapter import WhatsAppAdapter
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
