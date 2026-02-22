import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── In-memory demo store (used when Supabase is not configured) ─────
_demo_store: list[dict] = [
    {
        "id": str(uuid.uuid4()),
        "raw_url": f"https://www.instagram.com/p/design_mock_{i}/",
        "source": "instagram",
        "title": f"Amazing UI/UX Design Inspiration #{i}",
        "summary": "A brilliant showcase of UI/UX design concepts, featuring smooth animations, perfect spacing, and modern typography.",
        "category": "Design",
        "tags": ["ui", "ux", "design", "inspiration", "webdesign"],
        "thumbnail_url": f"https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&q=80&sig={i}",
        "author": f"design_guru_{i}",
        "processed": True,
        "created_at": (datetime.utcnow().replace(day=max(1, 28-i))).isoformat() + "Z",
        "sender_phone": "+1234567890",
    } for i in range(1, 41)
]

_use_demo_mode = True  # Flipped to False when real Supabase is connected

try:
    from supabase import create_client, Client
    _supabase_available = True
except ImportError:
    _supabase_available = False

_client = None


def _is_demo_mode() -> bool:
    """Return True if Supabase is not configured (placeholder values)."""
    url = os.getenv("SUPABASE_URL", "")
    return not url or "placeholder" in url or not _supabase_available


def get_supabase():
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
        _client = create_client(url, key)
    return _client


async def insert_link(data: dict) -> dict:
    if _is_demo_mode():
        record = {**data, "created_at": data.get("created_at", datetime.utcnow().isoformat())}
        _demo_store.insert(0, record)
        return record
    sb = get_supabase()
    result = sb.table("links").insert(data).execute()
    return result.data[0] if result.data else {}


async def get_links(limit: int = 100, offset: int = 0) -> list[dict]:
    if _is_demo_mode():
        return _demo_store[offset: offset + limit]
    sb = get_supabase()
    result = (
        sb.table("links")
        .select("*")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data or []


async def get_link_by_id(link_id: str) -> dict | None:
    if _is_demo_mode():
        return next((l for l in _demo_store if l["id"] == link_id), None)
    sb = get_supabase()
    result = sb.table("links").select("*").eq("id", link_id).execute()
    return result.data[0] if result.data else None


async def update_link(link_id: str, data: dict) -> dict:
    if _is_demo_mode():
        for i, link in enumerate(_demo_store):
            if link["id"] == link_id:
                _demo_store[i] = {**link, **data}
                return _demo_store[i]
        return {}
    sb = get_supabase()
    result = sb.table("links").update(data).eq("id", link_id).execute()
    return result.data[0] if result.data else {}


async def delete_link(link_id: str) -> bool:
    if _is_demo_mode():
        before = len(_demo_store)
        _demo_store[:] = [l for l in _demo_store if l["id"] != link_id]
        return len(_demo_store) < before
    sb = get_supabase()
    try:
        result = sb.table("links").delete().eq("id", link_id).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"Error deleting link {link_id}: {e}")
        return False


async def get_forgotten_gems(days_ago: int = 30) -> list[dict]:
    """Fetch links older than `days_ago` days for the Inspiration Roulette feature."""
    if _is_demo_mode():
        from datetime import timedelta
        cutoff = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
        return [l for l in _demo_store if l.get("processed") and l.get("created_at", "") < cutoff]
    sb = get_supabase()
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
    result = (
        sb.table("links")
        .select("*")
        .lt("created_at", cutoff)
        .eq("processed", True)
        .execute()
    )
    return result.data or []


# ── SQL migration (run once in Supabase SQL editor) ────────────────
MIGRATION_SQL = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS links (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  raw_url       TEXT NOT NULL,
  source        TEXT NOT NULL DEFAULT 'unknown',
  title         TEXT,
  summary       TEXT,
  category      TEXT,
  tags          TEXT[] DEFAULT '{}',
  thumbnail_url TEXT,
  author        TEXT,
  sender_phone  TEXT,
  processed     BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_links_category ON links(category);
CREATE INDEX IF NOT EXISTS idx_links_created_at ON links(created_at DESC);
"""
