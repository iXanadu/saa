"""Configuration loading for SAA."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class Config:
    """SAA configuration with hierarchical loading."""

    # Browser settings
    chromium_path: str = "/Applications/Chromium.app/Contents/MacOS/Chromium"
    headless: bool = True

    # Crawling settings
    pacing: str = "medium"  # off, low, medium, high
    max_pages: int = 50
    default_depth: int = 3

    # LLM settings
    default_llm: str = "xai:grok-4"
    xai_api_key: str = ""
    anthropic_api_key: str = ""

    # Mode settings
    mode: str = "own"  # own or competitor

    # Pacing delays (min, max) in seconds
    pacing_delays: dict = field(default_factory=lambda: {
        "off": (0, 0),
        "low": (0.5, 1.5),
        "medium": (1.0, 3.0),
        "high": (2.0, 5.0),
    })


def load_config() -> Config:
    """Load configuration from .env files with hierarchical precedence.

    Load order (later overrides earlier):
    1. Built-in defaults
    2. ~/.saa/.env (global user config)
    3. ~/.saa/.keys (global secrets)
    4. ./.env (project config)
    5. ./.keys (project secrets)
    """
    config = Config()

    # Global config
    global_dir = Path.home() / ".saa"
    if (global_dir / ".env").exists():
        load_dotenv(global_dir / ".env")
    if (global_dir / ".keys").exists():
        load_dotenv(global_dir / ".keys")

    # Project config
    load_dotenv(".env")
    load_dotenv(".keys")

    # Override from environment
    config.chromium_path = os.getenv("SAA_CHROMIUM_PATH", config.chromium_path)
    config.default_llm = os.getenv("SAA_DEFAULT_LLM", config.default_llm)
    config.xai_api_key = os.getenv("XAI_API_KEY", "")
    config.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    config.max_pages = int(os.getenv("SAA_MAX_PAGES", config.max_pages))
    config.default_depth = int(os.getenv("SAA_DEFAULT_DEPTH", config.default_depth))

    return config
