from datetime import datetime

from pydantic import BaseModel, Field


class FuelTransactionCreate(BaseModel):
    occurred_at: datetime | None = None
    vehicle_id: int = Field(gt=0)
    driver_id: int = Field(gt=0)
    fuel_site_id: int | None = Field(default=None, gt=0)
    odometer: int = Field(gt=0)
    gallons: float = Field(gt=0, le=500)
    price_per_gallon: float = Field(gt=0, le=100)
    source: str = Field(default="manual", max_length=32)
    card_last4: str | None = Field(default=None, min_length=4, max_length=4)
    notes: str | None = Field(default=None, max_length=512)


class FuelTransactionRead(BaseModel):
    id: int
    occurred_at: datetime
    vehicle_id: int
    driver_id: int
    fuel_site_id: int | None
    odometer: int
    gallons: float
    price_per_gallon: float
    source: str
    card_last4: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class FuelTransactionDetail(FuelTransactionRead):
    vehicle_unit: str
    driver_name: str
    fuel_site_name: str | None
