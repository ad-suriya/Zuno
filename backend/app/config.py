"""Runtime settings, read from environment variables.

On Cloud Run, secrets (e.g. SARVAM_API_KEY) are injected from Secret Manager as
environment variables with `--set-secrets`, so the app only ever reads env vars.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str
    google_cloud_project: str
    firestore_database: str
    firestore_emulator_host: str | None
    evidence_bucket: str | None
    cors_origins: tuple[str, ...]
    google_cloud_region: str = "asia-south1"
    llm_enabled: bool = False
    gemini_model: str = ""
    sarvam_api_key: str | None = None
    sarvam_stt_model: str = ""  # empty = Sarvam's current default model
    sarvam_tts_model: str = ""
    voice_rate_per_minute: int = 20
    # "memory" = in-process store for local demos without the Firestore emulator. Ignored on Cloud Run.
    repository: str = "firestore"

    @property
    def on_cloud_run(self) -> bool:
        return bool(os.environ.get("K_SERVICE"))


def _flag(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def get_settings() -> Settings:
    origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
    return Settings(
        environment=os.environ.get("ENVIRONMENT", "local"),
        google_cloud_project=os.environ.get("GOOGLE_CLOUD_PROJECT") or "zuno-local",
        firestore_database=os.environ.get("FIRESTORE_DATABASE", "(default)"),
        firestore_emulator_host=os.environ.get("FIRESTORE_EMULATOR_HOST") or None,
        evidence_bucket=os.environ.get("EVIDENCE_BUCKET") or None,
        cors_origins=tuple(o.strip() for o in origins.split(",") if o.strip()),
        google_cloud_region=os.environ.get("GOOGLE_CLOUD_REGION") or "asia-south1",
        llm_enabled=_flag("LLM_ENABLED"),
        gemini_model=os.environ.get("GEMINI_MODEL", "").strip(),
        sarvam_api_key=os.environ.get("SARVAM_API_KEY") or None,
        sarvam_stt_model=os.environ.get("SARVAM_STT_MODEL", "").strip(),
        sarvam_tts_model=os.environ.get("SARVAM_TTS_MODEL", "").strip(),
        voice_rate_per_minute=int(os.environ.get("VOICE_RATE_PER_MINUTE") or 20),
        repository=(os.environ.get("REPOSITORY") or "firestore").strip().lower(),
    )
