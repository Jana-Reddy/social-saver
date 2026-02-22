import re
from models.link import LinkSource

# ── URL Patterns ────────────────────────────────────────────────────
INSTAGRAM_PATTERNS = [
    r"https?://(?:www\.)?instagram\.com(?:/[A-Za-z0-9_\.]+)?/reel/[A-Za-z0-9_-]+/?",
    r"https?://(?:www\.)?instagram\.com(?:/[A-Za-z0-9_\.]+)?/p/[A-Za-z0-9_-]+/?",
    r"https?://(?:www\.)?instagram\.com(?:/[A-Za-z0-9_\.]+)?/tv/[A-Za-z0-9_-]+/?",
    r"https?://instagr\.am/[A-Za-z0-9_-]+/?",
]

TWITTER_PATTERNS = [
    r"https?://(?:www\.)?twitter\.com/\w+/status/\d+",
    r"https?://(?:www\.)?x\.com/\w+/status/\d+",
    r"https?://t\.co/[A-Za-z0-9]+",
]

GENERAL_URL_PATTERN = r"https?://[^\s<>\"'{}|\\^`\[\]]+"

INSTAGRAM_RE = re.compile("|".join(INSTAGRAM_PATTERNS), re.IGNORECASE)
TWITTER_RE = re.compile("|".join(TWITTER_PATTERNS), re.IGNORECASE)
GENERAL_URL_RE = re.compile(GENERAL_URL_PATTERN, re.IGNORECASE)


def classify_url(url: str) -> LinkSource:
    """Determine the source type of a URL."""
    if INSTAGRAM_RE.search(url):
        return LinkSource.instagram
    if TWITTER_RE.search(url):
        return LinkSource.twitter
    if GENERAL_URL_RE.search(url):
        return LinkSource.web
    return LinkSource.unknown


def extract_urls(text: str) -> list[dict]:
    """
    Extract all valid URLs from a text message.
    Returns a list of dicts: {url: str, source: LinkSource}
    Handles:
    - Multiple links in one message
    - Text + link mixed
    - Non-URL messages (returns empty list)
    """
    raw_urls = GENERAL_URL_RE.findall(text)
    results = []
    seen = set()
    for url in raw_urls:
        url = url.rstrip(".,;!?)")  # strip trailing punctuation
        if url in seen:
            continue
        seen.add(url)
        source = classify_url(url)
        results.append({"url": url, "source": source})
    return results


def sanitize_url(url: str) -> str:
    """Clean and normalize a URL."""
    url = url.strip()
    # Remove tracking params for Instagram
    if "instagram.com" in url:
        url = url.split("?")[0].rstrip("/") + "/"
    # Remove Twitter tracking
    if "twitter.com" in url or "x.com" in url:
        url = url.split("?")[0]
    return url


def is_valid_url(url: str) -> bool:
    """Quick validity check."""
    return bool(GENERAL_URL_RE.match(url))
