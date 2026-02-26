from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from typing import Iterable, List
from urllib.request import Request, urlopen

from .models import PageDocument


def load_documents_from_json(path: str | Path) -> List[PageDocument]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))

    docs: List[PageDocument] = []
    for item in payload:
        docs.append(
            PageDocument(
                title=item["title"],
                url=item["url"],
                content=item["content"],
                category=item.get("category", "general"),
            )
        )
    return docs


def _extract_title_and_text(html: str) -> tuple[str, str]:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    title = unescape(title_match.group(1).strip()) if title_match else "Untitled"

    cleaned = re.sub(r"<script[\\s\\S]*?</script>", " ", html, flags=re.IGNORECASE)
    cleaned = re.sub(r"<style[\\s\\S]*?</style>", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    text = unescape(" ".join(cleaned.split()))
    return title or "Untitled", text


def fetch_documents_from_urls(urls: Iterable[str], timeout_s: int = 15) -> List[PageDocument]:
    docs: List[PageDocument] = []

    for url in urls:
        req = Request(url, headers={"User-Agent": "PageIndexExampleBot/1.0"})
        with urlopen(req, timeout=timeout_s) as response:
            html = response.read().decode("utf-8", errors="ignore")
        title, text = _extract_title_and_text(html)
        docs.append(PageDocument(title=title, url=url, content=text, category="web"))

    return docs
