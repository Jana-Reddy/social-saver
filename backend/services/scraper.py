import os
import httpx
import asyncio
from models.link import LinkSource

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "instagram-scraper-api2.p.rapidapi.com")


async def scrape_instagram(url: str) -> dict:
    """Scrape Instagram post/reel metadata via RapidAPI."""
    if not RAPIDAPI_KEY:
        return {"error": "No RapidAPI key configured", "raw_text": url}

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }
    params = {"url": url}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://{RAPIDAPI_HOST}/v1/post_info",
                headers=headers,
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
            media = data.get("data", {})
            return {
                "caption": media.get("caption", ""),
                "thumbnail_url": media.get("thumbnail_url") or media.get("display_url", ""),
                "owner_username": media.get("owner", {}).get("username", ""),
                "raw_text": media.get("caption", ""),
            }
    except Exception as e:
        return {"error": str(e), "raw_text": url}


async def scrape_web(url: str) -> dict:
    """Extract readable content from a web page using httpx + BeautifulSoup."""
    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Social Saver Bot)"},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        # Try newspaper3k for rich extraction
        try:
            from newspaper import Article
            article = Article(url)
            article.set_html(html)
            article.parse()
            return {
                "title": article.title,
                "raw_text": article.text[:3000],  # cap at 3k chars
                "thumbnail_url": article.top_image or "",
                "author": ", ".join(article.authors) if article.authors else "",
            }
        except Exception:
            pass

        # Fallback: BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        title = soup.title.string if soup.title else ""
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        raw_text = " ".join(paragraphs)[:3000]
        og_image = ""
        og_tag = soup.find("meta", property="og:image")
        if og_tag:
            og_image = og_tag.get("content", "")
        return {"title": title, "raw_text": raw_text, "thumbnail_url": og_image, "author": ""}

    except Exception as e:
        return {"error": str(e), "raw_text": url, "title": "", "thumbnail_url": "", "author": ""}


async def scrape_twitter(url: str) -> dict:
    """Basic Twitter/X scrape — metadata only (no API required)."""
    try:
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Twitterbot/1.0"},
        ) as client:
            resp = await client.get(url)
            raw_text = f"Twitter/X link: {url}"
            return {"raw_text": raw_text, "title": "Twitter Post", "thumbnail_url": "", "author": ""}
    except Exception as e:
        return {"error": str(e), "raw_text": url, "title": "", "thumbnail_url": "", "author": ""}


async def scrape(url: str, source: LinkSource) -> dict:
    """Dispatch scraping based on source type."""
    if source == LinkSource.instagram:
        return await scrape_instagram(url)
    elif source == LinkSource.twitter:
        return await scrape_twitter(url)
    else:
        return await scrape_web(url)
