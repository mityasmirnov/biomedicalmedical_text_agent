from pydantic import BaseSettings
from typing import List

class UIConfig(BaseSettings):
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    # Add other UI-related configurations here

    class Config:
        env_file = ".env"
