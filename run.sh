#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

# Install deps once if the venv exists but libraries are missing.
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

exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
