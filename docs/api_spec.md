# Social Saver — API Specification

**Base URL**: `http://localhost:8000`  
**Docs UI**: `http://localhost:8000/docs` (Swagger / OpenAPI)  
**WebSocket**: `ws://localhost:8000/ws`

---

## Webhook Endpoints

### `POST /webhook/twilio`
Receives incoming WhatsApp messages from Twilio.

**Request** (form-data):
| Field | Type | Description |
|---|---|---|
| `From` | string | Sender's WhatsApp number e.g. `whatsapp:+919876543210` |
| `Body` | string | Message text (may contain URLs) |

**Response**: `200 OK` (plain text `"ok"`)

**Behavior**:
- Extracts all URLs from `Body`
- Sends ACK via WhatsApp: *"🔗 Link received! Analyzing the vibe... ✨"*
- Enqueues async pipeline: scrape → AI → DB → WebSocket broadcast

---

### `GET /webhook/meta`
Meta webhook verification challenge.

**Query Params**: `hub.verify_token`, `hub.challenge`, `hub.mode`  
**Response**: `200 OK` (echoes `hub.challenge`)

---

### `POST /webhook/meta`
Receives incoming WhatsApp messages from Meta Graph API.

**Request** (JSON): Standard Meta webhook payload  
**Response**: `200 {"status": "ok"}`

---

## Links Endpoints

### `GET /links/`
List all saved links.

**Query Params**:
| Param | Default | Description |
|---|---|---|
| `limit` | 100 | Max results (1–500) |
| `offset` | 0 | Pagination offset |
| `category` | — | Filter by category name |

**Response**:
```json
{
  "links": [
    {
      "id": "uuid",
      "raw_url": "https://...",
      "source": "instagram",
      "title": "AI-generated title",
      "summary": "2-3 sentence summary",
      "category": "Fitness",
      "tags": ["workout", "gym"],
      "thumbnail_url": "https://...",
      "author": "username",
      "processed": true,
      "created_at": "2024-02-19T15:30:00Z"
    }
  ],
  "count": 42
}
```

---

### `GET /links/roulette`
Returns a random forgotten gem.

**Query Params**:
| Param | Default | Description |
|---|---|---|
| `days_ago` | 30 | Links older than this many days |

**Response**: Single `LinkRecord` object

---

### `GET /links/{link_id}`
Get a specific link by ID.

**Response**: Single `LinkRecord` or `404`

---

### `DELETE /links/{link_id}`
Delete a saved link.

**Response**:
```json
{"deleted": true, "id": "uuid"}
```

---

## Export Endpoints

### `GET /export/markdown`
Download all saved links as a grouped Markdown file.

**Response**: `text/markdown` attachment  
**Filename**: `social_saver_export.md`

---

## WebSocket

### `ws://localhost:8000/ws`
Real-time event stream for the dashboard.

**Messages**:
```json
// New link received (before processing)
{"type": "link_added", "data": {"id": "uuid", "raw_url": "...", "source": "instagram"}}

// Link processed by AI
{"type": "link_updated", "data": { /* full LinkRecord */ }}
```

**Keepalive**: Send `"ping"` → server replies `"pong"`

---

## System Endpoints

### `GET /health`
```json
{"status": "ok", "service": "social-saver-backend"}
```

### `GET /`
```json
{"message": "Social Saver API 🔗", "docs": "/docs", "websocket": "/ws"}
```
