import os
from dataclasses import dataclass


@dataclass
class Settings:
    enable_llm: bool = os.getenv("ENABLE_LLM", "false").lower() == "true"
    llm_api_key: str = os.getenv("LLM_API_KEY", "")


settings = Settings()
