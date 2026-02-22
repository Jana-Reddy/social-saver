# System Architecture — Social Saver

## Pipeline Overview

```mermaid
flowchart TD
    A["📱 WhatsApp\n(User)"] -->|"Sends link"| B["🌐 WhatsApp Provider\n(Twilio / Meta Graph API)"]
    B -->|"HTTP POST"| C["⚡ FastAPI Webhook\n/webhook/twilio or /webhook/meta"]
    C -->|"ACK Reply\n'🔗 Link received! Analyzing...'"| B
    C -->|"Validate & Extract URLs\n(Regex Sanitizer)"| D{"URL Type?"}
    D -->|"Instagram"| E["📸 RapidAPI\nInstagram Scraper"]
    D -->|"Web / Blog"| F["🗞️ newspaper3k\n+ BeautifulSoup"]
    D -->|"Twitter/X"| G["🐦 Twitter\nMetadata Fetch"]
    E --> H["🧠 AI Synthesis\n(Gemini 1.5 Flash / GPT-4o)"]
    F --> H
    G --> H
    H -->|"JSON: title, summary, category, tags"| I["🗄️ Supabase\n(PostgreSQL)"]
    I -->|"Stored ✅"| J["📡 WebSocket Broadcast\n/ws"]
    J -->|"Real-time push"| K["🖥️ Next.js Dashboard\n(localhost:3000)"]
    K --> L["🔍 Fuzzy Search\n(Fuse.js)"]
    K --> M["📂 Category Buckets\n(Auto-sorted)"]
    K --> N["🎲 Inspiration Roulette\n(Forgotten Gems)"]
    K --> O["📥 Markdown Export"]
```

## Component Breakdown

| Component | Technology | Purpose |
|---|---|---|
| Webhook Receiver | FastAPI | Receives & ACKs WhatsApp messages |
| URL Sanitizer | Python regex | Classifies & cleans Instagram, Twitter, web URLs |
| Instagram Scraper | RapidAPI | Extracts caption, thumbnail, author |
| Web Scraper | newspaper3k + BS4 | Extracts readable text from blogs/articles |
| AI Orchestrator | Gemini 1.5 Flash | Returns `{title, summary, category, tags}` JSON |
| Database | Supabase (PostgreSQL) | Persists all saved links |
| WebSocket Server | FastAPI WS | Broadcasts real-time updates to dashboard |
| Dashboard | Next.js 14 + Tailwind | Masonry grid, search, filters, roulette, export |
| Search | Fuse.js | Client-side fuzzy search across all fields |

## Data Flow — Single Link

```
1. User sends "https://www.instagram.com/reel/ABC123/"
2. Webhook receives → extracts URL → detects Instagram
3. ACK sent: "🔗 Link received! Analyzing the vibe... ✨"
4. Background task: RapidAPI scrape → {caption, thumbnail, author}
5. Gemini synthesizes → {title, summary, category: "Fitness", tags: ["workout", "gym"]}
6. Saved to Supabase
7. WebSocket broadcasts to dashboard → card appears instantly
8. WhatsApp reply: "✅ Gym Motivation Reel\n📂 Fitness | 🏷️ workout, gym, motivation"
```
