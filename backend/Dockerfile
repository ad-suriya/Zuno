# Cloud Run image for the backend. Build from the REPO ROOT so prompts/ is included (F04):
#   docker build -f backend/Dockerfile -t zuno-backend .
# Cloud Run sets $PORT; secrets arrive as env vars via --set-secrets.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PROMPTS_DIR=/app/prompts SEBI_REGISTRY_PATH=/app/data/sebi_registry.csv
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/data ./data
COPY prompts ./prompts

RUN useradd --create-home zuno
USER zuno

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
