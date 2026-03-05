from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class FuelSite(TimestampMixin, Base):
    __tablename__ = "fuel_sites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tank_capacity_gallons: Mapped[float | None] = mapped_column(Float, nullable=True)
