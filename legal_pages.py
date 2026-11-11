import json
import mimetypes
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit


PUBLIC_PAGES = {"/", "/privacy", "/terms"}
PUBLIC_SITE_DIRECTORY = Path(__file__).parent / "legal_web" / "dist"
DOCUMENT_TABS_PATH = (
    Path(__file__).parent / "legal_web" / "src" / "data" / "documentTabs.json"
)
DEFAULT_TITLE = "Metagame Tracker Bot — Game community information, in Discord"
DEFAULT_DESCRIPTION = (
    "Metagame Tracker Bot helps game stores, event organizers, hubs, and players "
    "manage community event information in Discord."
)
PAGE_METADATA = {
    "/": (DEFAULT_TITLE, DEFAULT_DESCRIPTION),
    "/guide": ("SOP Guide — Metagame Tracker Bot", "Browse the Metagame Tracker Bot standard operating procedures."),
    "/privacy": ("Privacy Policy — MetaGameTracker Bot", "Privacy Policy for MetaGameTracker Bot."),
    "/terms": ("Terms of Service — MetaGameTracker Bot", "Terms of Service for MetaGameTracker Bot."),
}


@lru_cache(maxsize=1)
def _guide_page_names() -> frozenset[str]:
    with DOCUMENT_TABS_PATH.open(encoding="utf-8") as manifest_file:
        tabs = json.load(manifest_file)
    return frozenset(f"{tab['slug']}.html" for tab in tabs)


def get_legal_page(request_path: str) -> tuple[str, bytes] | None:
    route = urlsplit(request_path).path.rstrip("/") or "/"
    if route == "/guide":
        file_path = PUBLIC_SITE_DIRECTORY / "index.html"
    elif route.startswith("/guide/"):
        slug = route.removeprefix("/guide/")
        filename = f"{slug}.html"
        if "/" in slug or filename not in _guide_page_names():
            return None
        file_path = PUBLIC_SITE_DIRECTORY / "guides" / filename
    elif route in PUBLIC_PAGES:
        file_path = PUBLIC_SITE_DIRECTORY / "index.html"
    else:
        file_path = (PUBLIC_SITE_DIRECTORY / route.lstrip("/")).resolve()
        if not file_path.is_relative_to(PUBLIC_SITE_DIRECTORY.resolve()):
            return None

    if not file_path.is_file():
        return None

    content_type, _ = mimetypes.guess_type(file_path.name)
    content_type = content_type or "application/octet-stream"
    if content_type.startswith("text/") or content_type in {
        "application/javascript",
        "application/json",
    }:
        content_type += "; charset=utf-8"
    content = file_path.read_bytes()
    if route.startswith("/guide/"):
        section_link = (
            b'<nav aria-label="SOP navigation" style="max-width:960px;'
            b'margin:0 auto 18px;padding:14px 18px;border-bottom:1px solid #d4d0c3;'
            b'font:600 14px Arial,sans-serif"><a href="/guide" '
            b'style="color:#315b48;text-decoration:none">All SOP sections</a></nav>'
        )
        content = re.sub(
            br"(<body\b[^>]*>)",
            lambda match: match.group(1) + section_link,
            content,
            count=1,
            flags=re.IGNORECASE,
        )
    if route in PAGE_METADATA:
        title, description = PAGE_METADATA[route]
        content = content.replace(
            DEFAULT_TITLE.encode("utf-8"), title.encode("utf-8"), 1
        )
        content = content.replace(
            DEFAULT_DESCRIPTION.encode("utf-8"), description.encode("utf-8"), 1
        )
    return content_type, content
