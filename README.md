# ArXiv Research Agent

> **Read the full article:** [BLOG_POST_URL_HERE]

An autonomous AI agent that searches ArXiv, reads academic papers, and produces research summaries. Built with Google ADK and SurfaceDocs.

## Why This Exists

Every AI pipeline eventually generates something valuable, but there's never a clean place to put it. I've dumped JSON to GCS buckets, hacked together Apps Script bridges, built throwaway React apps. This project solves that by giving the agent a "publish" tool that produces a shareable document URL.

The agent runs headlessly via a FastAPI endpoint. You send it a research query, it searches ArXiv, reads relevant papers, synthesizes the findings, and saves a formatted document to SurfaceDocs. You get back a URL.

## How It Works

The agent has three tools:

1. **search_arxiv** - Search for papers by query and date range
2. **fetch_paper_content** - Read the full text of a paper via ar5iv.org
3. **save_document** - Save the final summary to SurfaceDocs

The agent decides how to use these tools to answer your query. It's capped at 5 ArXiv API calls to keep things bounded.

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for package management
- A Google API key (for Gemini)
- A SurfaceDocs API key (get one at [app.surfacedocs.dev](https://app.surfacedocs.dev))

### Installation

```bash
git clone https://github.com/GallagherSam/research-agent-surfacedocs
cd research-agent-surfacedocs
uv sync
```

### Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
GOOGLE_API_KEY=your_google_api_key
SURFACEDOCS_API_KEY=your_surfacedocs_api_key
SURFACEDOCS_FOLDER_ID=optional_folder_id
```

## Running

Start the server:

```bash
uv run uvicorn api.main:app --reload
```

Trigger a research run:

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "recent advances in AI agents", "days_back": 7, "max_papers": 10}'
```

Response:

```json
{
  "status": "success",
  "document_url": "https://app.surfacedocs.dev/d/...",
  "papers_analyzed": 4,
  "arxiv_calls_used": 2
}
```

The agent takes 30-60 seconds depending on how many papers it reads.

## API

### POST /research

Run the research agent.

**Request body:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| query | string | required | Research topic or question |
| days_back | int | 7 | How many days back to search |
| max_papers | int | 10 | Maximum papers to analyze |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | "success", "completed", or "error" |
| document_url | string | URL to the generated document |
| papers_analyzed | int | Number of papers the agent read in full |
| arxiv_calls_used | int | Number of ArXiv API calls made |
| error | string | Error message if something failed |

### GET /health

Health check endpoint.

## Project Structure

```
arxiv_research_agent/
├── agent.py              # ADK agent definition
├── config.py             # Settings from environment
├── models.py             # Pydantic models
├── tools/
│   ├── arxiv.py          # search_arxiv, fetch_paper_content
│   └── surfacedocs.py    # save_document
└── services/
    ├── arxiv_client.py   # ArXiv API client
    └── paper_fetcher.py  # ar5iv.org HTML fetcher

api/
├── main.py               # FastAPI app
├── routes.py             # /research endpoint
└── schemas.py            # Request/response models
```

## Built With

- [Google ADK](https://google.github.io/adk-docs/) - Agent Development Kit
- [SurfaceDocs](https://surfacedocs.dev) - Document output layer
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [uv](https://github.com/astral-sh/uv) - Package management

## License

MIT
