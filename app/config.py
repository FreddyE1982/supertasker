from dataclasses import dataclass
import os
from pathlib import Path

import yaml


@dataclass
class Settings:
    """Application configuration loaded from YAML with environment overrides."""

    api_url: str = "http://localhost:8000"


class ConfigLoader:
    """Load configuration from YAML and apply environment overrides."""

    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or os.getenv("CONFIG_FILE", "config.yaml"))

    def load(self) -> Settings:
        data: dict[str, str] = {}
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
            if isinstance(loaded, dict):
                data.update({str(k): str(v) for k, v in loaded.items()})
        if "API_URL" in os.environ:
            data["api_url"] = os.environ["API_URL"]
        return Settings(**{**Settings().__dict__, **data})
