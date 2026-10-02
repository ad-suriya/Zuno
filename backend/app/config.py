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

    @property
    def on_cloud_run(self) -> bool:
        return bool(os.environ.get("K_SERVICE"))


def get_settings() -> Settings:
    origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
    return Settings(
        environment=os.environ.get("ENVIRONMENT", "local"),
        google_cloud_project=os.environ.get("GOOGLE_CLOUD_PROJECT") or "zuno-local",
        firestore_database=os.environ.get("FIRESTORE_DATABASE", "(default)"),
        firestore_emulator_host=os.environ.get("FIRESTORE_EMULATOR_HOST") or None,
        evidence_bucket=os.environ.get("EVIDENCE_BUCKET") or None,
        cors_origins=tuple(o.strip() for o in origins.split(",") if o.strip()),
    )
