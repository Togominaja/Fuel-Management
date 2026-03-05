from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.fuel_transaction import FuelTransaction
from app.models.vehicle import Vehicle


def detect_anomalies(db: Session, transactions: list[FuelTransaction] | None = None) -> list[dict]:
    if transactions is None:
        transactions = (
            db.query(FuelTransaction)
            .join(Vehicle, Vehicle.id == FuelTransaction.vehicle_id)
            .order_by(FuelTransaction.vehicle_id, FuelTransaction.occurred_at)
            .all()
        )

    anomalies: list[dict] = []
    tx_by_vehicle: dict[int, list[FuelTransaction]] = defaultdict(list)

    for tx in transactions:
        tx_by_vehicle[tx.vehicle_id].append(tx)
        if tx.vehicle and tx.vehicle.tank_capacity_gallons:
            if tx.gallons > tx.vehicle.tank_capacity_gallons * 1.05:
                anomalies.append(
                    _alert(
                        "OVER_CAPACITY",
                        "high",
                        (
                            f"Fill amount {tx.gallons:.1f} exceeds vehicle capacity "
                            f"({tx.vehicle.tank_capacity_gallons:.1f} gal)."
                        ),
                        tx,
                    )
                )

    for vehicle_transactions in tx_by_vehicle.values():
        vehicle_transactions.sort(key=lambda item: item.occurred_at)
        for prev, current in zip(vehicle_transactions, vehicle_transactions[1:]):
            if current.odometer + 20 < prev.odometer:
                anomalies.append(
                    _alert(
                        "ODOMETER_ROLLBACK",
                        "critical",
                        (
                            f"Odometer dropped from {prev.odometer} to {current.odometer}."
                        ),
                        current,
                    )
                )

            minutes = (current.occurred_at - prev.occurred_at).total_seconds() / 60
            if minutes <= 120 and current.vehicle and current.vehicle.tank_capacity_gallons:
                combined = prev.gallons + current.gallons
                if combined > current.vehicle.tank_capacity_gallons * 1.15:
                    anomalies.append(
                        _alert(
                            "RAPID_REFUEL",
                            "medium",
                            (
                                f"Two refuels in {int(minutes)} min totaling {combined:.1f} gal."
                            ),
                            current,
                        )
                    )

            distance = current.odometer - prev.odometer
            if distance > 20:
                mpg = distance / current.gallons
                if mpg < 4:
                    anomalies.append(
                        _alert(
                            "LOW_EFFICIENCY",
                            "medium",
                            (
                                f"Estimated {mpg:.1f} mpg between fills; investigate leak/idling/theft."
                            ),
                            current,
                        )
                    )

    return anomalies


def _alert(code: str, severity: str, message: str, tx: FuelTransaction) -> dict:
    occurred_at = tx.occurred_at
    if isinstance(occurred_at, datetime):
        occurred_at_value = occurred_at.isoformat()
    else:
        occurred_at_value = str(occurred_at)

    return {
        "code": code,
        "severity": severity,
        "message": message,
        "transaction_id": tx.id,
        "vehicle_id": tx.vehicle_id,
        "driver_id": tx.driver_id,
        "occurred_at": occurred_at_value,
    }
