from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.driver import Driver
from app.models.fuel_site import FuelSite
from app.models.fuel_transaction import FuelTransaction
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle

settings = get_settings()

DEFAULT_ADMIN_EMAIL = settings.bootstrap_admin_email
DEFAULT_ADMIN_PASSWORD = settings.bootstrap_admin_password


def seed_data(db: Session) -> None:
    # Keep existing installs working if default admin email changes.
    for legacy_email in ("admin@fleetmvp.local", "admin@fleetmvp.io"):
        if legacy_email == DEFAULT_ADMIN_EMAIL:
            continue
        legacy_admin = db.query(User).filter(User.email == legacy_email).first()
        if legacy_admin:
            legacy_admin.email = DEFAULT_ADMIN_EMAIL
            db.commit()

    user_count = db.query(User).count()
    if user_count == 0:
        admin = User(
            email=DEFAULT_ADMIN_EMAIL,
            full_name="Fleet Admin",
            hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()

    if not settings.seed_demo_data:
        return

    if db.query(Driver).count() == 0:
        drivers = [
            Driver(name="Maria Ortega", license_number="CA-D-388201", card_tag="D1001"),
            Driver(name="James Cobb", license_number="CA-D-274761", card_tag="D1002"),
            Driver(name="Ivy Nguyen", license_number="CA-D-981142", card_tag="D1003"),
        ]
        db.add_all(drivers)
        db.commit()

    if db.query(Vehicle).count() == 0:
        vehicles = [
            Vehicle(unit_number="TRK-201", vin="1HGBH41JXMN109186", tank_capacity_gallons=32.0),
            Vehicle(unit_number="TRK-202", vin="2FTZF1729WCA12345", tank_capacity_gallons=28.0),
            Vehicle(unit_number="VAN-110", vin="1FTBR1Y89LKA54321", tank_capacity_gallons=24.0),
        ]
        db.add_all(vehicles)
        db.commit()

    if db.query(FuelSite).count() == 0:
        sites = [
            FuelSite(name="North Yard", location="Dallas, TX", tank_capacity_gallons=10000),
            FuelSite(name="South Yard", location="Fort Worth, TX", tank_capacity_gallons=8000),
        ]
        db.add_all(sites)
        db.commit()

    if db.query(FuelTransaction).count() == 0:
        drivers = db.query(Driver).order_by(Driver.id.asc()).all()
        vehicles = db.query(Vehicle).order_by(Vehicle.id.asc()).all()
        sites = db.query(FuelSite).order_by(FuelSite.id.asc()).all()
        if not drivers or not vehicles:
            return

        now = datetime.now(timezone.utc)
        data = [
            {
                "occurred_at": now - timedelta(days=4, hours=2),
                "vehicle_id": vehicles[0].id,
                "driver_id": drivers[0].id,
                "fuel_site_id": sites[0].id if sites else None,
                "odometer": 102120,
                "gallons": 24.5,
                "price_per_gallon": 3.89,
                "source": "card",
            },
            {
                "occurred_at": now - timedelta(days=2, hours=5),
                "vehicle_id": vehicles[1].id,
                "driver_id": drivers[1].id,
                "fuel_site_id": sites[1].id if len(sites) > 1 else None,
                "odometer": 88422,
                "gallons": 21.2,
                "price_per_gallon": 3.79,
                "source": "manual",
            },
            {
                "occurred_at": now - timedelta(days=1, hours=18),
                "vehicle_id": vehicles[2].id,
                "driver_id": drivers[2].id,
                "fuel_site_id": sites[0].id if sites else None,
                "odometer": 45910,
                "gallons": 18.9,
                "price_per_gallon": 3.92,
                "source": "card",
            },
            {
                "occurred_at": now - timedelta(hours=6),
                "vehicle_id": vehicles[0].id,
                "driver_id": drivers[0].id,
                "fuel_site_id": sites[0].id if sites else None,
                "odometer": 102280,
                "gallons": 36.5,
                "price_per_gallon": 3.95,
                "source": "manual",
            },
        ]

        db.add_all(FuelTransaction(**entry) for entry in data)
        db.commit()
