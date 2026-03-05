from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleRead

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleRead])
def list_vehicles(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Vehicle).order_by(Vehicle.unit_number.asc()).all()


@router.post("", response_model=VehicleRead)
def create_vehicle(
    payload: VehicleCreate,
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate unit number or VIN") from exc
    db.refresh(vehicle)
    return vehicle
