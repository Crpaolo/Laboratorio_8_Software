from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DinnerTransaction:

    amount: float
    card_number: str
    restaurant_code: str
    transaction_date: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if not self.card_number or len(self.card_number) < 8:
            raise ValueError("Card number must have at least 8 characters.")
        if not self.restaurant_code:
            raise ValueError("Restaurant code cannot be empty.")

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "card_number": self.card_number,
            "restaurant_code": self.restaurant_code,
            "transaction_date": self.transaction_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DinnerTransaction":
        return cls(
            amount=float(data["amount"]),
            card_number=data["card_number"],
            restaurant_code=data["restaurant_code"],
            transaction_date=datetime.fromisoformat(data["transaction_date"]),
        )
