from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="ArXiv Research Agent",
    description="AI agent for researching ArXiv papers and generating summaries",
    version="0.1.0",
)


# Include the research router
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "healthy"}
