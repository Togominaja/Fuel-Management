from datetime import datetime

from pydantic import BaseModel, Field


class VehicleBase(BaseModel):
    unit_number: str = Field(min_length=1, max_length=64)
    vin: str | None = Field(default=None, max_length=64)
    tank_capacity_gallons: float = Field(gt=0, le=500)
    status: str = Field(default="active", max_length=32)


class VehicleCreate(VehicleBase):
    pass


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
