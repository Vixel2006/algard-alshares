import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from gard.logger import get_logger

logger = get_logger(__name__)

_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path)


class Config:
    _instance: Optional["Config"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._gemini_api_key: Optional[str] = None
            self._initialized = True

    @property
    def gemini_api_key(self) -> Optional[str]:
        if self._gemini_api_key is None:
            self._gemini_api_key = os.environ.get("GEMINI_API_KEY")
            if self._gemini_api_key:
                logger.info("GEMINI_API_KEY loaded from .env file")
            else:
                logger.warning("GEMINI_API_KEY not found in .env file")
        return self._gemini_api_key

    @gemini_api_key.setter
    def gemini_api_key(self, value: str):
        self._gemini_api_key = value
        logger.info("GEMINI_API_KEY set")

    def validate(self) -> bool:
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY is not set")
            return False
        return True


def get_config() -> Config:
    return Config()
