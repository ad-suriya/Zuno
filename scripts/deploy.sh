#!/usr/bin/env bash
# Deploy Zuno to Cloud Run (F12). Run from the repo root.
#
#   PROJECT=my-gcp-project ./scripts/deploy.sh setup      # one-time: APIs, Firestore, service account, TTL, secret
#   PROJECT=my-gcp-project ./scripts/deploy.sh backend
#   PROJECT=my-gcp-project ./scripts/deploy.sh frontend   # after backend (needs its URL)
#   PROJECT=my-gcp-project ./scripts/deploy.sh all
#
# Optional env: REGION (asia-south1), GEMINI_MODEL, LLM_ENABLED (false), MIN_INSTANCES (0; use 1 during the demo),
# MAX_INSTANCES (3), AR_REPO (zuno).
set -euo pipefail

: "${PROJECT:?Set PROJECT to your GCP project id}"
REGION="${REGION:-asia-south1}"
AR_REPO="${AR_REPO:-zuno}"
SA_NAME="zuno-backend"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
BACKEND="zuno-backend"
FRONTEND="zuno-frontend"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-3}"
LLM_ENABLED="${LLM_ENABLED:-false}"
GEMINI_MODEL="${GEMINI_MODEL:-}"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT}/${AR_REPO}"

gc() { gcloud --project "$PROJECT" "$@"; }

# build <context-dir> <image> [docker build args...]: build with Cloud Build (no local Docker needed).
build() {
  local context="$1" image="$2"; shift 2
  local config; config="$(mktemp)"
  {
    echo "steps:"
    echo "- name: gcr.io/cloud-builders/docker"
    printf '  args: [build'
    for arg in "$@"; do printf ', "%s"' "$arg"; done
    printf ', -t, "%s", .]\n' "$image"
    echo "images: [\"$image\"]"
  } > "$config"
  gc builds submit "$context" --config="$config"
  rm -f "$config"
}

setup() {
  gc services enable run.googleapis.com firestore.googleapis.com aiplatform.googleapis.com \
    secretmanager.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

  gc firestore databases describe --database="(default)" >/dev/null 2>&1 \
    || gc firestore databases create --location="$REGION" --type=firestore-native

  # TTL: Firestore deletes documents once `expires_at` passes (7 days, PRIVACY.md). One policy per collection group.
  for group in investigations evidence signals verifications questions; do
    gc firestore fields ttls update expires_at --collection-group="$group" --enable-ttl --async || true
  done

  gc artifacts repositories describe "$AR_REPO" --location="$REGION" >/dev/null 2>&1 \
    || gc artifacts repositories create "$AR_REPO" --repository-format=docker --location="$REGION"

  gc iam service-accounts describe "$SA" >/dev/null 2>&1 \
    || gc iam service-accounts create "$SA_NAME" --display-name="Zuno backend"
  for role in roles/datastore.user roles/aiplatform.user roles/secretmanager.secretAccessor; do
    gc projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$SA" --role="$role" --condition=None >/dev/null
  done

  if ! gc secrets describe SARVAM_API_KEY >/dev/null 2>&1; then
    echo "Creating secret SARVAM_API_KEY. Paste the key, then press Ctrl-D:"
    gc secrets create SARVAM_API_KEY --replication-policy=automatic --data-file=-
  fi
  echo "Setup done. Also create a billing budget alert for the project in the Cloud Console."
}

backend() {
  local image="${REGISTRY}/${BACKEND}:$(git rev-parse --short HEAD)"
  # Build from the repo root so prompts/ and backend/data/ are in the image.
  build . "$image" -f backend/Dockerfile
  local frontend_url
  frontend_url="$(gc run services describe "$FRONTEND" --region "$REGION" --format='value(status.url)' 2>/dev/null || true)"
  gc run deploy "$BACKEND" --image "$image" --region "$REGION" --service-account "$SA" \
    --allow-unauthenticated --min-instances "$MIN_INSTANCES" --max-instances "$MAX_INSTANCES" \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_REGION=${REGION},LLM_ENABLED=${LLM_ENABLED},GEMINI_MODEL=${GEMINI_MODEL},CORS_ORIGINS=${frontend_url:-http://localhost:3000}" \
    --set-secrets "SARVAM_API_KEY=SARVAM_API_KEY:latest"
}

frontend() {
  local api_url image
  api_url="$(gc run services describe "$BACKEND" --region "$REGION" --format='value(status.url)')"
  image="${REGISTRY}/${FRONTEND}:$(git rev-parse --short HEAD)"
  build frontend "$image" --build-arg "NEXT_PUBLIC_API_BASE_URL=${api_url}"
  gc run deploy "$FRONTEND" --image "$image" --region "$REGION" --allow-unauthenticated \
    --min-instances "$MIN_INSTANCES" --max-instances "$MAX_INSTANCES"
  # The backend must allow the frontend origin.
  local web_url
  web_url="$(gc run services describe "$FRONTEND" --region "$REGION" --format='value(status.url)')"
  gc run services update "$BACKEND" --region "$REGION" --update-env-vars "CORS_ORIGINS=${web_url}"
  echo "Frontend: $web_url"
  echo "Backend:  $api_url"
  echo "Smoke:    API_BASE_URL=$api_url WEB_BASE_URL=$web_url make smoke"
}

case "${1:-}" in
  setup) setup ;;
  backend) backend ;;
  frontend) frontend ;;
  all) backend; frontend ;;
  *) echo "usage: PROJECT=<id> $0 setup|backend|frontend|all" >&2; exit 2 ;;
esac
