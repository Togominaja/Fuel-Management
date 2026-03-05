from pathlib import Path
import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from app.api import auth, dashboard, drivers, fuel_sites, fuel_transactions, vehicles
from app.core.config import get_settings
from app.db.base import Base
from app.db.bootstrap import seed_data
from app.db.session import SessionLocal, engine
from app.web.routes import router as web_router

settings = get_settings()
app = FastAPI(title=settings.app_name)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(web_router)
app.include_router(auth.router)
app.include_router(drivers.router)
app.include_router(vehicles.router)
app.include_router(fuel_sites.router)
app.include_router(fuel_transactions.router)
app.include_router(dashboard.router)

app_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(app_dir / "static")), name="static")


@app.on_event("startup")
def on_startup() -> None:
    last_error: Exception | None = None
    for attempt in range(1, 31):
        db = SessionLocal()
        try:
            Base.metadata.create_all(bind=engine)
            seed_data(db)
            return
        except (SQLAlchemyError, OSError) as exc:
            last_error = exc
            logger.warning("Database startup attempt %s/30 failed: %s", attempt, exc)
            time.sleep(2)
        finally:
            db.close()

    if last_error:
        raise RuntimeError("Database startup failed after retries") from last_error
