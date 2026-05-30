from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.dinner_transaction import DinnerTransaction
from domain.entities.reward import Reward


class MessagePublisher(ABC):

    @abstractmethod
    def publish(self, transaction: DinnerTransaction) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class MessageConsumer(ABC):

    @abstractmethod
    def start_consuming(self, callback) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


class RewardRepository(ABC):

    @abstractmethod
    def save(self, reward: Reward) -> None:
        pass

    @abstractmethod
    def find_by_card(self, card_number: str) -> List[Reward]:
        pass

    @abstractmethod
    def find_all(self) -> List[Reward]:
        pass

    @abstractmethod
    def total_points(self, card_number: str) -> int:
        pass

    @abstractmethod
    def total_cashback(self, card_number: str) -> float:
        pass
