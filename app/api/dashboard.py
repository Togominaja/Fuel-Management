from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.fuel_transaction import FuelTransaction
from app.schemas.dashboard import AnomalyAlert, DailyConsumption, DashboardSummary
from app.services.anomaly import detect_anomalies

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    days: int = Query(default=30, ge=1, le=365),
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    rows = db.query(FuelTransaction).filter(FuelTransaction.occurred_at >= cutoff).all()
    total_transactions = len(rows)
    total_gallons = sum(item.gallons for item in rows)
    total_spend = sum(item.gallons * item.price_per_gallon for item in rows)
    avg_price = (total_spend / total_gallons) if total_gallons else 0.0

    grouped = (
        db.query(
            func.date(FuelTransaction.occurred_at).label("day"),
            func.sum(FuelTransaction.gallons).label("gallons"),
            func.sum(FuelTransaction.gallons * FuelTransaction.price_per_gallon).label("spend"),
        )
        .filter(FuelTransaction.occurred_at >= cutoff)
        .group_by(func.date(FuelTransaction.occurred_at))
        .order_by(func.date(FuelTransaction.occurred_at))
        .all()
    )

    by_day = [
        DailyConsumption(
            day=str(row.day),
            gallons=round(float(row.gallons or 0), 2),
            spend=round(float(row.spend or 0), 2),
        )
        for row in grouped
    ]

    alerts = len(detect_anomalies(db, rows))

    return DashboardSummary(
        days=days,
        total_transactions=total_transactions,
        total_gallons=round(total_gallons, 2),
        total_spend=round(total_spend, 2),
        avg_price_per_gallon=round(avg_price, 3),
        alerts=alerts,
        by_day=by_day,
    )


@router.get("/anomalies", response_model=list[AnomalyAlert])
def list_anomalies(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(FuelTransaction)
        .order_by(FuelTransaction.occurred_at.desc())
        .limit(500)
        .all()
    )
    return [AnomalyAlert(**item) for item in detect_anomalies(db, rows)]
