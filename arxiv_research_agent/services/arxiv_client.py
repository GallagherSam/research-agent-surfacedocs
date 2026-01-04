"""ArXiv API client for searching research papers."""

import httpx
import feedparser
from datetime import datetime, timedelta, timezone

from arxiv_research_agent.models import Paper
from arxiv_research_agent.config import settings

ARXIV_API_URL = "https://export.arxiv.org/api/query"


class ArxivClient:
    """Client for fetching papers from arXiv API."""

    def __init__(self, timeout: float = 30.0):
        self._timeout = timeout
        self._categories = settings.arxiv_categories

    async def search(
        self,
        query: str,
        days_back: int = 7,
        max_results: int = 20,
    ) -> list[Paper]:
        """Search arXiv for papers matching query.

        Args:
            query: Search query (supports arXiv query syntax).
            days_back: Only return papers from last N days.
            max_results: Maximum papers to return.

        Returns:
            List of Paper objects.
        """
        search_query = self._build_query(query)
        url = self._build_url(search_query, max_results)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url)
            response.raise_for_status()

        return self._parse_response(response.text, days_back)

    def _build_query(self, query: str) -> str:
        """Build arXiv query with category filters."""
        cat_query = " OR ".join(f"cat:{cat}" for cat in self._categories)
        cat_query = f"({cat_query})"
        if query:
            return f"({query}) AND {cat_query}"
        return cat_query

    def _build_url(self, search_query: str, max_results: int) -> str:
        """Build full API URL."""
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{ARXIV_API_URL}?{query_string}"

    def _parse_response(self, xml_content: str, days_back: int) -> list[Paper]:
        """Parse Atom feed response into Paper objects."""
        feed = feedparser.parse(xml_content)
        papers = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        for entry in feed.entries:
            paper = self._parse_entry(entry)
            if paper and paper.published >= cutoff_date:
                papers.append(paper)

        return papers

    def _parse_entry(self, entry) -> Paper | None:
        """Parse single feed entry into Paper."""
        try:
            arxiv_id = entry.id.split("/abs/")[-1]
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            authors = [a.get("name", "") for a in entry.get("authors", [])]
            categories = [t.get("term", "") for t in entry.get("tags", [])]

            pdf_url = ""
            for link in entry.get("links", []):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href", "")
                    break

            return Paper(
                id=arxiv_id,
                title=" ".join(entry.title.split()),
                abstract=" ".join(entry.summary.split()),
                authors=authors,
                published=published,
                url=entry.link,
                pdf_url=pdf_url,
                categories=categories,
            )
        except (KeyError, AttributeError, ValueError):
            return None
