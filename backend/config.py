from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM providers
    cerebras_api_key: str
    groq_api_key: str
    sambanova_api_key: str
    openrouter_api_key: str

    # Tools
    tavily_api_key: str
    jina_api_key: str

    # App
    app_env: str = "dev"
    db_path: str = "./data/beat_reporter.db"
    chroma_path: str = "./data/chroma"

settings = Settings()