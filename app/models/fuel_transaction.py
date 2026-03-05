from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TransactionSource(str, Enum):
    MANUAL = "manual"
    CARD = "card"
    TELEMATICS = "telematics"


class FuelTransaction(Base):
    __tablename__ = "fuel_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    fuel_site_id: Mapped[int | None] = mapped_column(ForeignKey("fuel_sites.id"), nullable=True, index=True)
    odometer: Mapped[int] = mapped_column(Integer)
    gallons: Mapped[float] = mapped_column(Float)
    price_per_gallon: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(32), default=TransactionSource.MANUAL.value)
    card_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)

    vehicle = relationship("Vehicle")
    driver = relationship("Driver")
    fuel_site = relationship("FuelSite")
