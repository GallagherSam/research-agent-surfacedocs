"""API routes for the research agent."""

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from api.schemas import ResearchRequest, ResearchResponse
from arxiv_research_agent.agent import research_agent
from arxiv_research_agent.config import settings

router = APIRouter()

APP_NAME = "arxiv-research-agent"


@router.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest) -> ResearchResponse:
    """Execute the research agent with the given query.

    The agent will:
    1. Search arXiv for relevant papers
    2. Read promising papers in detail
    3. Synthesize findings into a document
    4. Save to surfacedocs and return the URL
    """
    # Create a unique session for this request
    user_id = "api_user"
    session_id = str(uuid4())

    # Set up session service and runner
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(
        agent=research_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Build the user message with query and parameters
    message_text = f"""Research query: {request.query}

Parameters:
- Search papers from the last {request.days_back} days
- Analyze up to {request.max_papers} papers

Please search arXiv, read relevant papers, and save a research summary document."""

    content = types.Content(
        role="user",
        parts=[types.Part(text=message_text)],
    )

    # Run the agent and collect results
    document_url = None
    error_message = None

    try:
        events = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        )

        async for event in events:
            # Check for tool results containing the document URL
            if hasattr(event, "tool_result") and event.tool_result:
                result = event.tool_result
                if isinstance(result, dict) and result.get("url"):
                    document_url = result["url"]

            # Alternative: Look for function call results in content parts
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    # Check if this is a function response
                    if hasattr(part, "function_response") and part.function_response:
                        response = part.function_response
                        if response.name == "save_document":
                            result = response.response
                            if isinstance(result, dict) and "url" in result:
                                document_url = result["url"]

            # Capture final response
            if event.is_final_response():
                # Agent has completed
                pass

    except Exception as e:
        error_message = str(e)

    # Get session state to extract metrics
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    state = session.state if session else {}
    arxiv_calls_used = state.get("arxiv_calls_used", 0)
    papers_read = state.get("papers_read", [])

    if error_message:
        return ResearchResponse(
            status="error",
            document_url=None,
            papers_analyzed=len(papers_read),
            arxiv_calls_used=arxiv_calls_used,
            error=error_message,
        )

    if not document_url:
        return ResearchResponse(
            status="completed",
            document_url=None,
            papers_analyzed=len(papers_read),
            arxiv_calls_used=arxiv_calls_used,
            error="Agent completed but no document was saved.",
        )

    return ResearchResponse(
        status="success",
        document_url=document_url,
        papers_analyzed=len(papers_read),
        arxiv_calls_used=arxiv_calls_used,
        error=None,
    )
