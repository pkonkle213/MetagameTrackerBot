from pathlib import Path
from urllib.parse import urlsplit


PUBLIC_PAGES = {
    "/": "home.html",
    "/privacy": "privacy.html",
    "/terms": "terms.html",
}
LEGAL_DIRECTORY = Path(__file__).parent / "legal"


def get_legal_page(request_path: str) -> tuple[str, bytes] | None:
    route = urlsplit(request_path).path.rstrip("/") or "/"
    filename = PUBLIC_PAGES.get(route)
    if filename is None:
        return None

    content = (LEGAL_DIRECTORY / filename).read_bytes()
    return "text/html; charset=utf-8", content
