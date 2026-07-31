from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:

    symbol: str

    direction: str

    quantity: int

    order_type: str

    price: float

    status: str = "PENDING"

    created_at: datetime = None

    filled_at: datetime = None

    filled_price: float = None