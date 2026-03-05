from datetime import datetime

from pydantic import BaseModel, Field


class FuelSiteBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    tank_capacity_gallons: float | None = Field(default=None, gt=0, le=100000)


class FuelSiteCreate(FuelSiteBase):
    pass


class FuelSiteRead(FuelSiteBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
