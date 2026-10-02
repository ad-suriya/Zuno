# F12: Deployment (GCP)

| Effort | Phase | Depends on | Touches |
|---|---|---|---|
| Medium | 0 (basic), 5 (full) | — | infra scripts, Dockerfiles, docs |

## Goal

A stable public URL for the demo, deployed early and redeployed after every
phase, so cloud issues surface well before demo day.

## Phase 0: basic (do first)

- GCP project, region `asia-south1`.
- Firestore **Native mode** database.
- Backend → Cloud Run from `backend/Dockerfile` (already exists).
- Frontend → Cloud Run (Next.js standalone output) or Vercel. Set `NEXT_PUBLIC_API_BASE_URL`
  at build time.
- `CORS_ORIGINS` = the frontend URL.
- `scripts/deploy.sh` (or Makefile `deploy-backend` / `deploy-frontend`) using `gcloud run deploy`.

## Phase 5: full

| Item | Detail |
|---|---|
| Service account | Dedicated SA for the backend: `roles/datastore.user`, `roles/aiplatform.user` (F04), `roles/secretmanager.secretAccessor` |
| Secrets | `SARVAM_API_KEY` in Secret Manager → `--set-secrets` |
| Prompts | Build from repo root so `prompts/` is in the image (see F04) |
| Retention | Firestore TTL policy. Needs an `expires_at` timestamp field on investigation + subcollection docs (e.g. created_at + 7 days); TTL deletes when that time passes. Add the field in `models.py`. |
| Scaling | `--min-instances=1` during the demo window (avoid cold start), `--max-instances` small |
| Smoke | `API_BASE_URL=… WEB_BASE_URL=… make smoke` against prod |
| Budget | Billing alert on the project |
| Demo safety | Keep `LLM_ENABLED` switchable via env var for instant fallback on stage |

## Tasks

- [ ] Project + Firestore + APIs enabled (Run, Firestore, Vertex AI, Secret Manager)
- [ ] Frontend Dockerfile (standalone) or Vercel config
- [ ] Deploy scripts / Make targets
- [ ] Service account + IAM
- [ ] Secret Manager wiring
- [ ] `expires_at` + TTL policy
- [ ] Prod smoke run + README "Deploying" section
- [ ] `ARCHITECTURE.md` GCP section with the actual layout

## Acceptance criteria

- `make smoke` passes against the deployed URLs.
- A fresh team member can deploy using only the README.
- No secret appears in the repo, image, or frontend bundle.
