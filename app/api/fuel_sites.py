from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.fuel_site import FuelSite
from app.schemas.fuel_site import FuelSiteCreate, FuelSiteRead

router = APIRouter(prefix="/api/fuel-sites", tags=["fuel-sites"])


@router.get("", response_model=list[FuelSiteRead])
def list_fuel_sites(
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(FuelSite).order_by(FuelSite.name.asc()).all()


@router.post("", response_model=FuelSiteRead)
def create_fuel_site(
    payload: FuelSiteCreate,
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    site = FuelSite(**payload.model_dump())
    db.add(site)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate site name") from exc
    db.refresh(site)
    return site
