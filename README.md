# Fleet Command MVP

WSL-runnable fleet fuel management MVP that includes:

- JWT auth with role-aware user model
- Core entities: drivers, vehicles, fuel sites, fuel transactions
- Dashboard metrics (transactions, gallons, spend)
- Basic anomaly detection (over-capacity fills, odometer rollback, rapid refuel, low efficiency)
- Simple web UI for login, transaction entry, and alert review

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite (local dev) or PostgreSQL (hosted)

## Quick Start (WSL)

```bash
cd "/mnt/c/Dev/Automated Fuel Management"
./run.sh
```

Open `http://127.0.0.1:8000`
(`run.sh` auto-creates `.env` and generates a random `SECRET_KEY` on first run.)

Default login:

- Email: `sbravatti.nelson@gmail.com`
- Password: `ChangeMe123!`

## API Notes

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET/POST /api/drivers`
- `GET/POST /api/vehicles`
- `GET/POST /api/fuel-sites`
- `GET/POST /api/fuel-transactions`
- `GET /api/dashboard/summary?days=30`
- `GET /api/dashboard/anomalies`

## Tests

```bash
cd "/mnt/c/Dev/Automated Fuel Management"
source .venv/bin/activate
pytest -q
```

## Share Public Demo Link

Use this to create a temporary public URL you can share with collaborators:

```bash
cd "/mnt/c/Dev/Automated Fuel Management"
./share-link.sh
```

Notes:

- It prints a `https://...trycloudflare.com` link plus login credentials.
- It rotates the admin password each time for safer sharing.
- Keep that terminal running; press `Ctrl+C` to stop the public link.

## Permanent Hosted Link (Recommended)

For a stable URL your brother can access any time, deploy to Render with `render.yaml`.

1. Push this project to GitHub.
2. In Render, create a new Blueprint and select this repo.
3. Render will provision:
- `automated-fuel-management` web app
- managed PostgreSQL database
4. After first deploy, open the service URL shown in Render (stable URL).
5. In Render dashboard, copy `BOOTSTRAP_ADMIN_PASSWORD` env var and log in with `sbravatti.nelson@gmail.com`.

Notes:

- This is persistent hosting. Your machine can be off and the app stays online.
- `SEED_DEMO_DATA` is set to `false` in hosted mode by default.
- For a custom domain, add it in Render service settings.

## Next Expansion Paths

1. Add PostgreSQL + migrations (Alembic)
2. Add multi-tenant company support
3. Integrate telematics APIs and card processors
4. Add granular RBAC and audit logs
5. Add dispatch/work order and maintenance modules
