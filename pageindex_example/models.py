from dataclasses import dataclass


@dataclass
class PageDocument:
    title: str
    url: str
    content: str
    category: str = "general"


@dataclass
class IndexedChunk:
    chunk_id: str
    page_title: str
    page_url: str
    category: str
    text: str
