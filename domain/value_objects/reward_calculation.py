from dataclasses import dataclass


POINTS_PER_UNIT = 10
CASHBACK_RATE = 0.05
MIN_AMOUNT_FOR_BONUS = 100.0
BONUS_POINTS = 50


@dataclass(frozen=True)
class RewardCalculation:

    points: int
    cashback: float

    @classmethod
    def from_amount(cls, amount: float) -> "RewardCalculation":
        if amount <= 0:
            raise ValueError("Amount must be greater than zero to calculate rewards.")

        base_points = int(amount * POINTS_PER_UNIT)
        bonus = BONUS_POINTS if amount >= MIN_AMOUNT_FOR_BONUS else 0
        total_points = base_points + bonus

        cashback = round(amount * CASHBACK_RATE, 2)

        return cls(points=total_points, cashback=cashback)
