from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverRead

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


@router.get("", response_model=list[DriverRead])
def list_drivers(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Driver).order_by(Driver.name.asc()).all()


@router.post("", response_model=DriverRead)
def create_driver(
    payload: DriverCreate,
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    driver = Driver(**payload.model_dump())
    db.add(driver)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate license or card tag") from exc
    db.refresh(driver)
    return driver
