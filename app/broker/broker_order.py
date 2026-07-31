from dataclasses import dataclass
from datetime import datetime


@dataclass
class BrokerOrder:

    order_id: int

    symbol: str

    direction: str

    quantity: int

    price: float

    status: str = "PENDING"

    created_at: datetime = None

    filled_at: datetime = None