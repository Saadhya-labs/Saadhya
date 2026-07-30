from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:

    symbol: str

    direction: str

    quantity: int

    entry_price: float

    stop_loss: float

    target: float

    entry_time: datetime

    exit_price: float | None = None

    exit_time: datetime | None = None

    status: str = "OPEN"

    pnl: float = 0.0