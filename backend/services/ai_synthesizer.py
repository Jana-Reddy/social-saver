import os
import json
from models.link import AIResult, Category

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

VALID_CATEGORIES = [c.value for c in Category]

SYSTEM_PROMPT = """You are a content curator AI. Given raw text from a web page, blog, social media post, or URL, extract structured metadata.

Return ONLY valid JSON with this exact schema:
{
  "title": "concise, engaging title (max 80 chars)",
  "summary": "2-3 sentence summary of the content",
  "category": "one of: Coding, Design, Fitness, Food, Travel, Finance, Science, Entertainment, News, Other",
  "tags": ["tag1", "tag2", "tag3"]  // 3-7 relevant tags, lowercase
}

Rules:
- title must be a proper English title, not a URL
- summary must be informative and specific
- category must be EXACTLY one of the listed options
- tags must be lowercase, 1-3 words each
- Return ONLY the JSON object, no markdown code blocks, no extra text
"""


async def synthesize_with_gemini(raw_text: str, url: str) -> AIResult:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"URL: {url}\n\nContent:\n{raw_text[:4000]}"
    response = model.generate_content(
        [{"role": "user", "parts": [SYSTEM_PROMPT + "\n\n" + prompt]}]
    )
    text = response.text.strip()
    return _parse_ai_response(text)


async def synthesize_with_openai(raw_text: str, url: str) -> AIResult:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    prompt = f"URL: {url}\n\nContent:\n{raw_text[:4000]}"
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    return _parse_ai_response(text)


def _parse_ai_response(text: str) -> AIResult:
    """Parse AI JSON output, with fallback for malformed responses."""
    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        data = json.loads(text)
        # Validate category
        cat = data.get("category", "Other")
        if cat not in VALID_CATEGORIES:
            cat = "Other"
        return AIResult(
            title=data.get("title", "Untitled")[:80],
            summary=data.get("summary", ""),
            category=cat,
            tags=data.get("tags", [])[:7],
        )
    except json.JSONDecodeError:
        # Fallback result
        return AIResult(
            title="Saved Link",
            summary="Content saved for later review.",
            category=Category.other,
            tags=["saved"],
        )


async def synthesize(raw_text: str, url: str) -> AIResult:
    """Orchestrate AI synthesis. Tries primary provider, falls back to the other."""
    if AI_PROVIDER == "openai" and OPENAI_API_KEY:
        try:
            return await synthesize_with_openai(raw_text, url)
        except Exception:
            pass

    if GEMINI_API_KEY:
        try:
            return await synthesize_with_gemini(raw_text, url)
        except Exception:
            pass

    # Hard fallback
    return AIResult(
        title="Saved Content",
        summary="AI synthesis unavailable. Content saved.",
        category=Category.other,
        tags=["unprocessed"],
    )
