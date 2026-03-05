from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    unit_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    vin: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    tank_capacity_gallons: Mapped[float] = mapped_column(Float, default=20.0)
    status: Mapped[str] = mapped_column(String(32), default="active")
