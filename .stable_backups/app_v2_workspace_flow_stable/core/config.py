import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class AppConfig:
    name: str
    env: str
    host: str
    port: int

@dataclass(frozen=True)
class DatabaseConfig:
    url: str

@dataclass(frozen=True)
class ExecutorConfig:
    default_executor: str
    openclaw_mode: str

@dataclass(frozen=True)
class LLMConfig:
    enabled: bool
    provider: str
    model: str
    openai_api_key: str

@dataclass(frozen=True)
class Settings:
    app: AppConfig
    database: DatabaseConfig
    executor: ExecutorConfig
    llm: LLMConfig

def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}

def load_settings() -> Settings:
    app = AppConfig(
        name=os.getenv("APP_NAME", "AutoFabric"),
        env=os.getenv("APP_ENV", "local"),
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "8000")),
    )

    database = DatabaseConfig(
        url=os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/autofabric"),
    )

    executor = ExecutorConfig(
        default_executor=os.getenv("DEFAULT_EXECUTOR", "openclaw"),
        openclaw_mode=os.getenv("OPENCLAW_MODE", "bridge"),
    )

    llm = LLMConfig(
        enabled=_to_bool(os.getenv("LLM_ENABLED", "false")),
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    )

    return Settings(app=app, database=database, executor=executor, llm=llm)

settings = load_settings()
