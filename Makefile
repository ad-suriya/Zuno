# Local development. Run each long-running target in its own terminal:
#   make emulator   make backend   make frontend
# The Firestore emulator needs Java 21+ on PATH.

EMULATOR_HOST ?= localhost:8080

.PHONY: setup emulator backend frontend test smoke

setup:
	test -f .env || cp .env.example .env
	test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local
	cd backend && python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt
	cd frontend && npm install

emulator:
	gcloud emulators firestore start --host-port=$(EMULATOR_HOST)

backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000 --env-file ../.env

frontend:
	cd frontend && npm run dev

test:
	cd backend && FIRESTORE_EMULATOR_HOST=$(EMULATOR_HOST) .venv/bin/python -m pytest -q
	cd frontend && npm run lint && npx tsc --noEmit

smoke:
	./tests/smoke.sh
