import os
import httpx

try:
    from twilio.rest import Client as TwilioClient
    _twilio_available = True
except ImportError:
    _twilio_available = False
    TwilioClient = None  # type: ignore

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
WEBHOOK_PROVIDER = os.getenv("WEBHOOK_PROVIDER", "twilio")


async def send_whatsapp_message(to: str, message: str) -> bool:
    """Send a WhatsApp message via Twilio or Meta Graph API."""
    if WEBHOOK_PROVIDER == "meta":
        return await _send_via_meta(to, message)
    return _send_via_twilio(to, message)


def _send_via_twilio(to: str, message: str) -> bool:
    if not _twilio_available or not TWILIO_ACCOUNT_SID or "placeholder" in TWILIO_ACCOUNT_SID:
        print(f"[WhatsApp Demo] Would send to {to}: {message}")
        return True
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # Normalize number format
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"
        client.messages.create(body=message, from_=TWILIO_WHATSAPP_NUMBER, to=to)
        return True
    except Exception as e:
        print(f"[WhatsApp] Twilio send error: {e}")
        return False


async def _send_via_meta(to: str, message: str) -> bool:
    if not META_ACCESS_TOKEN or not META_PHONE_NUMBER_ID:
        print("[WhatsApp] Meta credentials not configured")
        return False
    # Strip whatsapp: prefix if present
    to = to.replace("whatsapp:", "").replace("+", "")
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": message},
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages",
                headers={"Authorization": f"Bearer {META_ACCESS_TOKEN}"},
                json=payload,
            )
            resp.raise_for_status()
            return True
    except Exception as e:
        print(f"[WhatsApp] Meta send error: {e}")
        return False
