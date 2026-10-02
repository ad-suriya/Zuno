#!/usr/bin/env bash
# End-to-end smoke test against a running local stack (emulator + backend + frontend).
# Unit and API tests live in backend/tests.
set -euo pipefail

API="${API_BASE_URL:-http://localhost:8000}"
WEB="${WEB_BASE_URL:-http://localhost:3000}"

check() { printf '%-40s' "$1"; }

check "backend /health"
curl -fsS "$API/health" | grep -q '"status":"ok"' && echo ok

check "backend /health/ready (Firestore)"
curl -fsS "$API/health/ready" | grep -q '"firestore":"ok"' && echo ok

check "CORS for frontend origin"
curl -fsS -o /dev/null -D - -H "Origin: $WEB" "$API/health" | grep -qi "access-control-allow-origin: $WEB" && echo ok

check "create + assess investigation"
id=$(curl -fsS -X POST "$API/api/v1/investigations" -H 'Content-Type: application/json' \
  -d '{"story":"Guaranteed 20% monthly returns. Share the OTP 123456.","channel":"telegram"}' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); assert "123456" not in d["evidence"][0]["content"]; print(d["investigation"]["id"])')
curl -fsS -X POST "$API/api/v1/investigations/$id/assessment" | grep -q '"level":"HIGH_CONCERN"' && echo ok

check "add evidence + re-assess (F01) with next steps (F02)"
curl -fsS -X POST "$API/api/v1/investigations/$id/evidence" -H 'Content-Type: application/json' \
  -d '{"content":"Pay 2000 rupees to withdraw your profit."}' | grep -q '"WITHDRAWAL_FEE"'
curl -fsS -X POST "$API/api/v1/investigations/$id/assessment" | grep -q '"NEVER_SHARE_CREDENTIALS"' && echo ok

check "error shape for unknown investigation"
curl -sS "$API/api/v1/investigations/does-not-exist" | grep -q '"code":"NOT_FOUND"' && echo ok

check "frontend /"
curl -fsS "$WEB/" | grep -q "Zuno" && echo ok

echo "All smoke checks passed."
