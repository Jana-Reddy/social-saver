import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Form, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse

from services.sanitizer import extract_urls, sanitize_url
from services.scraper import scrape
from services.ai_synthesizer import synthesize
from services.whatsapp import send_whatsapp_message
from db.supabase_client import insert_link, update_link
from models.link import LinkSource

router = APIRouter(prefix="/webhook", tags=["webhook"])

META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "social_saver_token")
WEBHOOK_PROVIDER = os.getenv("WEBHOOK_PROVIDER", "twilio")


# ── Pipeline ─────────────────────────────────────────────────────────
async def process_link_pipeline(link_id: str, url: str, source: LinkSource, sender: str, broadcast_fn):
    """Full async pipeline: scrape → AI → DB update → WebSocket broadcast."""
    try:
        # 1. Scrape
        scraped = await scrape(url, source)
        raw_text = scraped.get("raw_text", url)
        thumbnail = scraped.get("thumbnail_url", "")
        author = scraped.get("author", "") or scraped.get("owner_username", "")

        # 2. AI Synthesis
        ai_result = await synthesize(raw_text, url)

        # 3. Update DB
        update_data = {
            "title": ai_result.title,
            "summary": ai_result.summary,
            "category": ai_result.category,
            "tags": ai_result.tags,
            "thumbnail_url": thumbnail,
            "author": author,
            "processed": True,
        }
        updated = await update_link(link_id, update_data)

        # 4. Broadcast via WebSocket
        await broadcast_fn({"type": "link_updated", "data": updated})

        # 5. Notify user via WhatsApp
        if sender:
            msg = (
                f"✅ *{ai_result.title}*\n"
                f"📂 {ai_result.category} | 🏷️ {', '.join(ai_result.tags[:3])}\n"
                f"_{ai_result.summary[:120]}..._"
            )
            await send_whatsapp_message(sender, msg)

    except Exception as e:
        print(f"[Pipeline] Error processing {url}: {e}")
        await update_link(link_id, {"processed": False})


# ── Twilio Webhook ────────────────────────────────────────────────────
@router.post("/twilio")
async def twilio_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(...),
):
    broadcast = request.app.state.broadcast
    sender = From  # e.g. "whatsapp:+919876543210"

    urls = extract_urls(Body)
    if not urls:
        await send_whatsapp_message(sender, "🤔 Hmm, I couldn't find a link in that message. Try sending a URL!")
        return PlainTextResponse("ok")

    # ACK immediately
    await send_whatsapp_message(sender, "🔗 Link received! Analyzing the vibe... ✨")

    for item in urls:
        url = sanitize_url(item["url"])
        source = item["source"]
        link_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Insert placeholder record
        await insert_link({
            "id": link_id,
            "raw_url": url,
            "source": source,
            "sender_phone": sender,
            "processed": False,
            "created_at": now,
        })

        # Broadcast new card immediately
        await broadcast({"type": "link_added", "data": {"id": link_id, "raw_url": url, "source": source}})

        # Process in background
        background_tasks.add_task(
            process_link_pipeline, link_id, url, source, sender, broadcast
        )

    return PlainTextResponse("ok")


# ── Meta Graph API Webhook ────────────────────────────────────────────
@router.get("/meta")
async def meta_verify(request: Request):
    """Webhook verification challenge for Meta."""
    params = dict(request.query_params)
    if params.get("hub.verify_token") == META_VERIFY_TOKEN:
        return PlainTextResponse(params.get("hub.challenge", ""))
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/meta")
async def meta_webhook(request: Request, background_tasks: BackgroundTasks):
    broadcast = request.app.state.broadcast
    body = await request.json()
    try:
        entry = body["entry"][0]
        change = entry["changes"][0]
        value = change["value"]
        messages = value.get("messages", [])
        if not messages:
            return {"status": "no messages"}

        msg = messages[0]
        sender = msg["from"]
        text = msg.get("text", {}).get("body", "")

        urls = extract_urls(text)
        if not urls:
            await send_whatsapp_message(f"+{sender}", "🤔 I couldn't find a link. Try sending a URL!")
            return {"status": "no url"}

        await send_whatsapp_message(f"+{sender}", "🔗 Link received! Analyzing the vibe... ✨")

        for item in urls:
            url = sanitize_url(item["url"])
            source = item["source"]
            link_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            await insert_link({
                "id": link_id,
                "raw_url": url,
                "source": source,
                "sender_phone": sender,
                "processed": False,
                "created_at": now,
            })
            await broadcast({"type": "link_added", "data": {"id": link_id, "raw_url": url, "source": source}})
            background_tasks.add_task(
                process_link_pipeline, link_id, url, source, f"+{sender}", broadcast
            )
    except (KeyError, IndexError) as e:
        print(f"[Meta] Parse error: {e}")

    return {"status": "ok"}
