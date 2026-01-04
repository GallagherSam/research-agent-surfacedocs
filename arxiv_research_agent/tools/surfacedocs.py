"""Surfacedocs tool for saving research output."""

from surfacedocs import SurfaceDocs

from arxiv_research_agent.config import settings


async def save_document(document: dict) -> dict:
    """Save the research document to Surfacedocs.

    Call this once you have synthesized your findings into a complete document.
    The document must follow the Surfacedocs block structure as specified in
    the system prompt.

    Args:
        document: A document dict with required 'title' and 'blocks' keys,
                  and optional 'metadata' key. Structure:
                  {
                    "title": "Document title",
                    "metadata": {
                      "source": "research-agent",
                      "tags": ["optional", "tags"]
                    },
                    "blocks": [
                      {"type": "heading", "content": "Section", "metadata": {"level": 1}},
                      {"type": "paragraph", "content": "Body text..."},
                      {"type": "list", "content": "- Item 1\\n- Item 2", "metadata": {"listType": "bullet"}},
                      {"type": "code", "content": "code here", "metadata": {"language": "python"}},
                      {"type": "quote", "content": "A quote."},
                      {"type": "table", "content": "| Col1 | Col2 |\\n|------|------|\\n| a | b |"},
                      {"type": "divider", "content": ""}
                    ]
                  }

    Returns:
        Dict with 'status', 'url', and 'message'.
    """
    # Add default metadata if not provided
    if "metadata" not in document:
        document["metadata"] = {"source": "arxiv-research-agent"}

    client = SurfaceDocs(api_key=settings.surfacedocs_api_key)

    result = client.save(
        document,
        folder_id=settings.surfacedocs_folder_id,
    )

    return {
        "status": "success",
        "url": result.url,
        "message": "Document saved successfully.",
    }
