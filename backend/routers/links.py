from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Request
from pydantic import BaseModel
import uuid
import random
from datetime import datetime
from db.supabase_client import get_links, get_link_by_id, delete_link, get_forgotten_gems, insert_link
from services.sanitizer import sanitize_url, extract_urls
from routers.webhook import process_link_pipeline

router = APIRouter(prefix="/links", tags=["links"])


@router.get("/")
async def list_links(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    category: str | None = None,
):
    """Get all saved links, optionally filtered by category."""
    links = await get_links(limit=limit, offset=offset)
    if category:
        links = [l for l in links if l.get("category") == category]
    return {"links": links, "count": len(links)}


@router.get("/roulette")
async def inspiration_roulette(days_ago: int = Query(30, ge=1)):
    """Return a random forgotten gem from more than `days_ago` days ago."""
    gems = await get_forgotten_gems(days_ago=days_ago)
    if not gems:
        # Fall back to any random link
        all_links = await get_links(limit=100)
        if not all_links:
            raise HTTPException(status_code=404, detail="No links saved yet!")
        gems = all_links
    return random.choice(gems)


@router.get("/{link_id}")
async def get_link(link_id: str):
    link = await get_link_by_id(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.delete("/{link_id}")
async def remove_link(link_id: str):
    success = await delete_link(link_id)
    if not success:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"deleted": True, "id": link_id}

class LinkRequest(BaseModel):
    url: str

@router.post("/")
async def add_link_manually(req: LinkRequest, request: Request, background_tasks: BackgroundTasks):
    urls = extract_urls(req.url)
    if not urls:
        raise HTTPException(status_code=400, detail="No valid URL found")
    
    item = urls[0]
    url = sanitize_url(item["url"])
    source = item["source"]
    link_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    link_data = {
        "id": link_id,
        "raw_url": url,
        "source": source,
        "sender_phone": "web_manual",
        "processed": False,
        "created_at": now,
    }
    await insert_link(link_data)
    
    broadcast = request.app.state.broadcast
    await broadcast({"type": "link_added", "data": link_data})
    
    background_tasks.add_task(
        process_link_pipeline, link_id, url, source, "web_manual", broadcast
    )
    
    return {"status": "ok", "id": link_id}
