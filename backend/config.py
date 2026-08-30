from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE_PATH", "./data/negotiagent.db")
    max_rounds: int = 3
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    @property
    def openai_enabled(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))


settings = Settings()
