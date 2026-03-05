#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p .share

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

if ! python -c "import fastapi, sqlalchemy, pydantic_settings" >/dev/null 2>&1; then
  pip install -r requirements.txt
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

if grep -q "replace-with-a-long-random-string" .env; then
  python - <<'PY'
import secrets
from pathlib import Path

env_path = Path(".env")
content = env_path.read_text(encoding="utf-8")
env_path.write_text(
    content.replace("replace-with-a-long-random-string", secrets.token_urlsafe(48)),
    encoding="utf-8",
)
PY
fi

if [ ! -x ./cloudflared ]; then
  curl -L --fail --silent --show-error \
    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64" \
    -o ./cloudflared
  chmod +x ./cloudflared
fi

APP_LOG=".share/app.log"
TUNNEL_LOG=".share/tunnel.log"
rm -f "$APP_LOG" "$TUNNEL_LOG"

pkill -f "uvicorn app.main:app --host 127.0.0.1 --port 8000" >/dev/null 2>&1 || true
pkill -f "cloudflared tunnel --url http://127.0.0.1:8000" >/dev/null 2>&1 || true

uvicorn app.main:app --host 127.0.0.1 --port 8000 >"$APP_LOG" 2>&1 &
APP_PID=$!

cleanup() {
  kill "$TUNNEL_PID" >/dev/null 2>&1 || true
  kill "$APP_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

for _ in $(seq 1 30); do
  if curl -sSf "http://127.0.0.1:8000/health" >/dev/null; then
    break
  fi
  sleep 1
done

if ! curl -sSf "http://127.0.0.1:8000/health" >/dev/null; then
  echo "App failed to start. See $APP_LOG"
  exit 1
fi

ADMIN_EMAIL="$(python - <<'PY'
from app.core.config import get_settings
print(get_settings().bootstrap_admin_email)
PY
)"

SHARE_PASSWORD="${1:-$(python - <<'PY'
import secrets
print("Demo!" + secrets.token_hex(4))
PY
)}"

python - <<'PY' "$SHARE_PASSWORD" "$ADMIN_EMAIL"
import sys

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User

password = sys.argv[1]
admin_email = sys.argv[2]
db = SessionLocal()
try:
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        raise SystemExit("Admin user not found")
    admin.hashed_password = get_password_hash(password)
    db.commit()
finally:
    db.close()
PY

./cloudflared tunnel --no-autoupdate --url "http://127.0.0.1:8000" >"$TUNNEL_LOG" 2>&1 &
TUNNEL_PID=$!

URL=""
for _ in $(seq 1 40); do
  URL=$(grep -Eo 'https://[-a-zA-Z0-9]+\.trycloudflare\.com' "$TUNNEL_LOG" | head -n1 || true)
  if [ -n "$URL" ]; then
    break
  fi
  sleep 1
done

if [ -z "$URL" ]; then
  echo "Tunnel failed to start. See $TUNNEL_LOG"
  exit 1
fi

echo ""
echo "Public URL: $URL"
echo "Login email: $ADMIN_EMAIL"
echo "Login password: $SHARE_PASSWORD"
echo ""
echo "Press Ctrl+C to stop sharing."

wait "$TUNNEL_PID"
