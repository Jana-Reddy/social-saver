🚀 Task List: Project "Social Saver" (Production-Grade)
🏗️ Architecture: The "Sync-to-Knowledge" Pipeline

Goal: Build a resilient event-driven system that handles social links and converts them into structured, searchable JSON.

🛠️ Phase 1: Ingest & Webhook (The Entry Point)
Senior Focus: Don't just receive links—validate and sanitize them.

[ ] Webhook Infrastructure: Deploy a FastAPI (Python) or Express (Node) endpoint using Ngrok or Cloudflare Tunnels.

[ ] WhatsApp Provider Setup: Configure Twilio Sandbox or Meta Graph API.

[ ] Input Sanitization: - [ ] Regex validation for Instagram Reels/Posts, X/Twitter, and standard URLs.

[ ] Handle "Edge Cases": Multiple links in one message, text + link, or non-URL messages.

[ ] Response UX: Implement immediate "Ack" (Acknowledgment) messages: "🔗 Link received! Analyzing the vibe..."

🧠 Phase 2: Scraper & AI Synthesis (The Intelligence)
Senior Focus: Use asynchronous processing to prevent timeout errors.

[ ] Data Extraction Engine:

[ ] Instagram: Use a reliable Scraper (RapidAPI or Playwright) to pull caption, thumbnail_url, and owner_username.

[ ] Web Content: Use newspaper3k or Cheerio to extract the "Readability" content from blogs.

[ ] AI Orchestration (The Brain):

[ ] Design a System Prompt for Gemini/GPT-4o to return strictly formatted JSON.

[ ] Schema: { "title": str, "summary": str, "category": enum[Coding, Design, Fitness, etc.], "tags": list[str] }.

[ ] State Management: Connect to Supabase (PostgreSQL) or Firebase for persistence.

🖥️ Phase 3: The "Discovery" Dashboard (Frontend)
Senior Focus: Focus on "Scannability" and Search performance.

[x] Modern Dark UI: Build a responsive dark-theme Next.js dashboard matching the InstaSave Hub aesthetic.

[x] Smart Components:

  [x] Metrics Row: 5 stat cards with glowing icons (Total Saves, Instagram, Twitter/X, Articles, Favorites).

  [x] Header Bar: Wide search input, filter icon, and gradient 'Random' button.

  [x] Masonry Grid: Dark cards with colored top-borders, pill tags, and clean action icons.

⚡ Phase 4: The "Wow" Factor (Anti-Gravity Features)
Senior Focus: Features that prove this is a "Product," not just a "Project."

[ ] Auto-Categorization: The UI should automatically sort links into "Buckets" based on AI tags.

[ ] "Inspiration Roulette": A button that resurfaces a "Forgotten Gem" from 30+ days ago.

[ ] Bulk Export: A "Download as Notion Page" or "Markdown" button for researchers.

📦 Final Deliverables Checklist (Submission Ready)
System Architecture Diagram: * Requirement: A clear Mermaid.js or PDF diagram showing the flow from WhatsApp → Webhook → LLM → DB → Dashboard.

The "Golden Thread" Demo Video:

Requirement: A 2-minute high-def recording. Show the phone screen (sending a link), the bot's instant reply, and the website updating in real-time (use WebSockets if possible for that "live" feel).

Production Codebase:

Requirement: GitHub URL with a clean README.md, .env.example, and a docker-compose.yml (for that Senior Dev flair).

The "API Spec":

Requirement: A short document or Swagger/Postman collection showing your API endpoints.