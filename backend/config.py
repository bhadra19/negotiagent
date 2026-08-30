from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE_PATH", "./data/negotiagent.db")
    max_rounds: int = 3


settings = Settings()

