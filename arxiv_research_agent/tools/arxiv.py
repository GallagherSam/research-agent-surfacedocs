"""ArXiv tools for the research agent."""

from google.adk.tools import ToolContext

from arxiv_research_agent.services import ArxivClient, PaperFetcher
from arxiv_research_agent.config import settings


async def search_arxiv(
    query: str,
    days_back: int,
    max_results: int,
    tool_context: ToolContext,
) -> dict:
    """Search arXiv for research papers matching the query.

    Use this tool to find papers on a topic. You can refine searches
    based on initial results. Each call counts toward the limit.

    Args:
        query: Search query. Supports keywords, phrases, and arXiv syntax
               like "ti:transformer" (title) or "au:bengio" (author).
        days_back: How many days back to search (1-30).
        max_results: Maximum papers to return (1-50).

    Returns:
        Dict with 'papers' list and 'calls_remaining' count.
    """
    # Track API calls
    calls_used = tool_context.state.get("arxiv_calls_used", 0)
    max_calls = settings.max_arxiv_calls

    if calls_used >= max_calls:
        return {
            "status": "error",
            "error": f"ArXiv API call limit reached ({max_calls} calls max).",
            "calls_remaining": 0,
        }

    # Increment call counter
    tool_context.state["arxiv_calls_used"] = calls_used + 1

    client = ArxivClient()
    papers = await client.search(
        query=query,
        days_back=min(days_back, 30),
        max_results=min(max_results, 50),
    )

    return {
        "status": "success",
        "papers": [
            {
                "id": p.id,
                "title": p.title,
                "abstract": p.abstract[:500] + "..." if len(p.abstract) > 500 else p.abstract,
                "authors": p.authors[:5],
                "published": p.published.isoformat(),
                "url": p.url,
            }
            for p in papers
        ],
        "total_found": len(papers),
        "calls_remaining": max_calls - calls_used - 1,
    }


async def fetch_paper_content(arxiv_id: str, tool_context: ToolContext) -> dict:
    """Fetch the full text content of a paper from ar5iv.org.

    Use this to read the complete paper when the abstract isn't enough.
    Only fetch papers that seem highly relevant based on search results.

    Args:
        arxiv_id: The arXiv paper ID (e.g., "2401.12345" or "2401.12345v1").

    Returns:
        Dict with paper title and full text content.
    """
    fetcher = PaperFetcher()
    content = await fetcher.fetch(arxiv_id)

    if content is None:
        return {
            "status": "error",
            "error": f"Could not fetch paper {arxiv_id}. It may not have an HTML version.",
        }

    # Track which papers we've read
    papers_read = tool_context.state.get("papers_read", [])
    papers_read.append(arxiv_id)
    tool_context.state["papers_read"] = papers_read

    return {
        "status": "success",
        "paper_id": content.paper_id,
        "title": content.title,
        "content": content.content
    }