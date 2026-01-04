"""Fetch full paper content from ar5iv.org."""

import httpx
import re
from arxiv_research_agent.models import PaperContent


class PaperFetcher:
    """Fetches and extracts text from ar5iv HTML papers."""

    AR5IV_BASE = "https://ar5iv.org/html"

    def __init__(self, timeout: float = 60.0):
        self._timeout = timeout

    async def fetch(self, arxiv_id: str) -> PaperContent | None:
        """Fetch paper content from ar5iv.

        Args:
            arxiv_id: ArXiv paper ID (e.g., "2401.12345").

        Returns:
            PaperContent with extracted text, or None if unavailable.
        """
        url = f"{self.AR5IV_BASE}/{arxiv_id}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

            content = self._extract_text(response.text)
            title = self._extract_title(response.text)

            return PaperContent(
                paper_id=arxiv_id,
                title=title,
                content=content,
            )
        except httpx.HTTPError:
            return None

    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML, removing tags and scripts."""
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)

        # Limit length to avoid token explosion
        return text.strip()[:50000]

    def _extract_title(self, html: str) -> str:
        """Extract title from HTML."""
        match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Unknown Title"
