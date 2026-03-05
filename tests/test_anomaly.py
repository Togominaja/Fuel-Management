from datetime import datetime, timedelta, timezone

from app.models.fuel_transaction import FuelTransaction
from app.models.vehicle import Vehicle
from app.services.anomaly import detect_anomalies


def test_anomaly_detection_flags_over_capacity_and_rollback():
    vehicle = Vehicle(id=1, unit_number="TRK-1", tank_capacity_gallons=20.0, status="active")
    base_time = datetime.now(timezone.utc)

    tx1 = FuelTransaction(
        id=1,
        occurred_at=base_time,
        vehicle_id=1,
        driver_id=1,
        fuel_site_id=None,
        odometer=1000,
        gallons=10,
        price_per_gallon=3.5,
        source="manual",
    )
    tx1.vehicle = vehicle

    tx2 = FuelTransaction(
        id=2,
        occurred_at=base_time + timedelta(hours=1),
        vehicle_id=1,
        driver_id=1,
        fuel_site_id=None,
        odometer=900,
        gallons=22,
        price_per_gallon=3.5,
        source="manual",
    )
    tx2.vehicle = vehicle

    alerts = detect_anomalies(None, [tx1, tx2])
    codes = {item["code"] for item in alerts}

    assert "OVER_CAPACITY" in codes
    assert "ODOMETER_ROLLBACK" in codes
