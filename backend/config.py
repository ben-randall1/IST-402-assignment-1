"""Local configuration helpers for the backend service."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def geoapify_api_key() -> str | None:
    """Return the configured Geoapify key without exposing its value."""
    load_dotenv(ENV_FILE)
    value = os.getenv("GEOAPIFY_API_KEY")
    return value.strip() if value and value.strip() else None
