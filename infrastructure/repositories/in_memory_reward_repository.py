from typing import List

from application.interfaces.ports import RewardRepository
from domain.entities.reward import Reward


class InMemoryRewardRepository(RewardRepository):

    def __init__(self) -> None:
        self._store: List[Reward] = []

    def save(self, reward: Reward) -> None:
        self._store.append(reward)

    def find_by_card(self, card_number: str) -> List[Reward]:
        return [r for r in self._store if r.card_number == card_number]

    def find_all(self) -> List[Reward]:
        return list(self._store)

    def total_points(self, card_number: str) -> int:
        return sum(r.points for r in self.find_by_card(card_number))

    def total_cashback(self, card_number: str) -> float:
        return round(sum(r.cashback for r in self.find_by_card(card_number)), 2)

    def clear(self) -> None:
        self._store.clear()
