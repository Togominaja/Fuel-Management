from pydantic import BaseModel


class DailyConsumption(BaseModel):
    day: str
    gallons: float
    spend: float


class DashboardSummary(BaseModel):
    days: int
    total_transactions: int
    total_gallons: float
    total_spend: float
    avg_price_per_gallon: float
    alerts: int
    by_day: list[DailyConsumption]


class AnomalyAlert(BaseModel):
    code: str
    severity: str
    message: str
    transaction_id: int
    vehicle_id: int
    driver_id: int
    occurred_at: str
