from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.driver import Driver
from app.models.fuel_site import FuelSite
from app.models.fuel_transaction import FuelTransaction
from app.models.vehicle import Vehicle
from app.schemas.fuel_transaction import FuelTransactionCreate, FuelTransactionDetail, FuelTransactionRead

router = APIRouter(prefix="/api/fuel-transactions", tags=["fuel-transactions"])


@router.get("", response_model=list[FuelTransactionDetail])
def list_fuel_transactions(
    limit: int = Query(default=100, ge=1, le=500),
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(FuelTransaction, Vehicle, Driver, FuelSite)
        .join(Vehicle, Vehicle.id == FuelTransaction.vehicle_id)
        .join(Driver, Driver.id == FuelTransaction.driver_id)
        .outerjoin(FuelSite, FuelSite.id == FuelTransaction.fuel_site_id)
        .order_by(FuelTransaction.occurred_at.desc())
        .limit(limit)
        .all()
    )

    response: list[FuelTransactionDetail] = []
    for tx, vehicle, driver, site in transactions:
        response.append(
            FuelTransactionDetail(
                **FuelTransactionRead.model_validate(tx).model_dump(),
                vehicle_unit=vehicle.unit_number,
                driver_name=driver.name,
                fuel_site_name=site.name if site else None,
            )
        )
    return response


@router.post("", response_model=FuelTransactionRead)
def create_fuel_transaction(
    payload: FuelTransactionCreate,
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).first():
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if not db.query(Driver).filter(Driver.id == payload.driver_id).first():
        raise HTTPException(status_code=404, detail="Driver not found")
    if payload.fuel_site_id and not db.query(FuelSite).filter(FuelSite.id == payload.fuel_site_id).first():
        raise HTTPException(status_code=404, detail="Fuel site not found")

    tx = FuelTransaction(
        occurred_at=payload.occurred_at or datetime.now(timezone.utc),
        vehicle_id=payload.vehicle_id,
        driver_id=payload.driver_id,
        fuel_site_id=payload.fuel_site_id,
        odometer=payload.odometer,
        gallons=payload.gallons,
        price_per_gallon=payload.price_per_gallon,
        source=payload.source,
        card_last4=payload.card_last4,
        notes=payload.notes,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
