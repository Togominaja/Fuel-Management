from datetime import datetime

from pydantic import BaseModel, Field


class DriverBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    license_number: str = Field(min_length=3, max_length=64)
    card_tag: str | None = Field(default=None, max_length=64)
    active: bool = True


class DriverCreate(DriverBase):
    pass


class DriverRead(DriverBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
