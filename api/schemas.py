from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Request to run research agent."""

    query: str = Field(..., description="Research query or topic")
    max_papers: int = Field(default=10, ge=1, le=50)
    days_back: int = Field(default=7, ge=1, le=30)


class ResearchResponse(BaseModel):
    """Response from research agent."""

    status: str
    document_url: str | None = None
    papers_analyzed: int
    arxiv_calls_used: int
    error: str | None = None
