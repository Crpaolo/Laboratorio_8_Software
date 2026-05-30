from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Reward:

    card_number: str
    points: int
    cashback: float
    restaurant_code: str
    original_amount: float
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.points < 0:
            raise ValueError("Points cannot be negative.")
        if self.cashback < 0:
            raise ValueError("Cashback cannot be negative.")
        if not self.card_number:
            raise ValueError("Card number cannot be empty.")

    def to_dict(self) -> dict:
        return {
            "card_number": self.card_number,
            "points": self.points,
            "cashback": self.cashback,
            "restaurant_code": self.restaurant_code,
            "original_amount": self.original_amount,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reward":
        return cls(
            card_number=data["card_number"],
            points=int(data["points"]),
            cashback=float(data["cashback"]),
            restaurant_code=data["restaurant_code"],
            original_amount=float(data["original_amount"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
