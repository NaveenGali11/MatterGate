"""Server-only configuration. Never serialize this object."""
import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv()


@dataclass(frozen=True)
class Settings:
    public_demo: bool = field(default_factory=lambda: os.getenv("MATTERGATE_PUBLIC_DEMO", "false").lower() == "true")
    public_origin: str = field(default_factory=lambda: os.getenv("MATTERGATE_PUBLIC_ORIGIN", "").rstrip("/"))
    live_enabled: bool = field(default_factory=lambda: os.getenv("MATTERGATE_LIVE_ENABLED", "true").lower() == "true")
    live_daily_limit: int = field(default_factory=lambda: max(0, int(os.getenv("MATTERGATE_LIVE_DAILY_LIMIT", "100"))))
    live_monthly_limit: int = field(default_factory=lambda: max(0, int(os.getenv("MATTERGATE_LIVE_MONTHLY_LIMIT", "1000"))))
    database: str = field(default_factory=lambda: os.getenv("MATTERGATE_DATABASE", "data/mattergate.sqlite3"))
    session_secret: str = field(default_factory=lambda: os.getenv("MATTERGATE_SESSION_SECRET") or secrets.token_urlsafe(32))
    api_key: str = field(default_factory=lambda: os.getenv("NEBIUS_API_KEY", "").strip(), repr=False)
    base_url: str = field(default_factory=lambda: os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1").rstrip("/"))
    model: str = field(default_factory=lambda: os.getenv("NEBIUS_MODEL", "nvidia/Nemotron-3_5-Lightning"))
    timeout: float = field(default_factory=lambda: min(45, max(1, float(os.getenv("MODEL_TIMEOUT_SECONDS", "45")))))
    max_tokens: int = field(default_factory=lambda: min(900, max(128, int(os.getenv("MODEL_MAX_OUTPUT_TOKENS", "900")))))
    temperature: float = field(default_factory=lambda: min(1, max(0, float(os.getenv("MODEL_TEMPERATURE", "0.1")))))

    def __post_init__(self):
        if self.public_demo:
            origin = urlsplit(self.public_origin)
            if (origin.scheme != "https" or not origin.hostname or origin.username or origin.password
                    or origin.path or origin.query or origin.fragment or origin.port not in (None, 443)
                    or len(self.session_secret) < 32):
                raise ValueError("Public demo requires an HTTPS origin and a stable, strong session secret")

    @property
    def live_ready(self) -> bool:
        url = urlsplit(self.base_url)
        return bool(self.live_enabled and self.api_key and self.model.startswith("nvidia/") and url.scheme == "https"
                    and url.hostname in {"api.tokenfactory.nebius.com", "api.tokenfactory.us-central1.nebius.com"}
                    and not url.username and not url.password and url.path.rstrip("/") == "/v1"
                    and not url.query and not url.fragment and url.port in (None, 443))
