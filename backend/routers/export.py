from fastapi import APIRouter
from db.supabase_client import get_links

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/markdown")
async def export_markdown():
    """Export all saved links as a Markdown document."""
    links = await get_links(limit=500)
    lines = [
        "# 🔖 Social Saver — My Knowledge Base\n",
        f"> Exported {len(links)} links\n",
        "---\n",
    ]

    # Group by category
    from collections import defaultdict
    categories: dict[str, list] = defaultdict(list)
    for link in links:
        cat = link.get("category") or "Uncategorized"
        categories[cat].append(link)

    for category, items in sorted(categories.items()):
        lines.append(f"\n## 📂 {category}\n")
        for item in items:
            title = item.get("title") or item.get("raw_url", "Untitled")
            url = item.get("raw_url", "")
            summary = item.get("summary", "")
            tags = item.get("tags", [])
            tag_str = " ".join(f"`#{t}`" for t in tags) if tags else ""
            lines.append(f"### [{title}]({url})\n")
            if summary:
                lines.append(f"{summary}\n")
            if tag_str:
                lines.append(f"{tag_str}\n")
            lines.append("\n")

    markdown = "\n".join(lines)
    from fastapi.responses import Response
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=social_saver_export.md"},
    )
