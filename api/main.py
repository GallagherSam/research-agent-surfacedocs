from fastapi import FastAPI

app = FastAPI(
    title="ArXiv Research Agent",
    description="AI agent for researching ArXiv papers and generating summaries",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "healthy"}
