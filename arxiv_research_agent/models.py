from datetime import datetime

from pydantic import BaseModel


class Paper(BaseModel):
    """ArXiv paper metadata."""

    id: str
    title: str
    abstract: str
    authors: list[str]
    published: datetime
    url: str
    pdf_url: str
    categories: list[str]


class PaperContent(BaseModel):
    """Full paper content from HTML."""

    paper_id: str
    title: str
    content: str  # Cleaned text from HTML


class SearchResult(BaseModel):
    """Result from ArXiv search."""

    papers: list[Paper]
    query: str
    total_found: int
