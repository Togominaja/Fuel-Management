from app.schemas.auth import Token
from app.schemas.dashboard import AnomalyAlert, DashboardSummary
from app.schemas.driver import DriverCreate, DriverRead
from app.schemas.fuel_site import FuelSiteCreate, FuelSiteRead
from app.schemas.fuel_transaction import FuelTransactionCreate, FuelTransactionDetail, FuelTransactionRead
from app.schemas.user import UserRead
from app.schemas.vehicle import VehicleCreate, VehicleRead

__all__ = [
    "Token",
    "UserRead",
    "DriverCreate",
    "DriverRead",
    "VehicleCreate",
    "VehicleRead",
    "FuelSiteCreate",
    "FuelSiteRead",
    "FuelTransactionCreate",
    "FuelTransactionRead",
    "FuelTransactionDetail",
    "DashboardSummary",
    "AnomalyAlert",
]
