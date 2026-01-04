from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Google AI
    google_api_key: str

    # Surfacedocs
    surfacedocs_api_key: str
    surfacedocs_folder_id: str | None = None

    # Agent settings
    max_arxiv_calls: int = 5
    default_days_back: int = 7
    default_max_papers: int = 10

    # ArXiv categories to search
    arxiv_categories: list[str] = ["cs.AI", "cs.LG", "cs.CL", "cs.MA"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
