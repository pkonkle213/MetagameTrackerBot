import mimetypes
from pathlib import Path
from urllib.parse import urlsplit


PUBLIC_PAGES = {"/", "/privacy", "/terms"}
PUBLIC_SITE_DIRECTORY = Path(__file__).parent / "legal_web" / "dist"
DEFAULT_TITLE = "Metagame Tracker Bot — Game community information, in Discord"
DEFAULT_DESCRIPTION = (
    "Metagame Tracker Bot helps game stores, event organizers, hubs, and players "
    "manage community event information in Discord."
)
PAGE_METADATA = {
    "/": (DEFAULT_TITLE, DEFAULT_DESCRIPTION),
    "/privacy": ("Privacy Policy — MetaGameTracker Bot", "Privacy Policy for MetaGameTracker Bot."),
    "/terms": ("Terms of Service — MetaGameTracker Bot", "Terms of Service for MetaGameTracker Bot."),
}


def get_legal_page(request_path: str) -> tuple[str, bytes] | None:
    route = urlsplit(request_path).path.rstrip("/") or "/"
    if route in PUBLIC_PAGES:
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
    if route in PAGE_METADATA:
        title, description = PAGE_METADATA[route]
        content = content.replace(
            DEFAULT_TITLE.encode("utf-8"), title.encode("utf-8"), 1
        )
        content = content.replace(
            DEFAULT_DESCRIPTION.encode("utf-8"), description.encode("utf-8"), 1
        )
    return content_type, content
