from application.interfaces.ports import RewardRepository
from domain.entities.dinner_transaction import DinnerTransaction
from domain.entities.reward import Reward
from domain.value_objects.reward_calculation import RewardCalculation


class ProcessRewardUseCase:

    def __init__(self, repository: RewardRepository) -> None:
        self._repository = repository

    def execute(self, transaction: DinnerTransaction) -> Reward:
        calculation = RewardCalculation.from_amount(transaction.amount)

        reward = Reward(
            card_number=transaction.card_number,
            points=calculation.points,
            cashback=calculation.cashback,
            restaurant_code=transaction.restaurant_code,
            original_amount=transaction.amount,
            created_at=transaction.transaction_date,
        )

        self._repository.save(reward)
        return reward

    def get_account_summary(self, card_number: str) -> dict:
        return {
            "card_number": card_number,
            "total_points": self._repository.total_points(card_number),
            "total_cashback": self._repository.total_cashback(card_number),
            "reward_count": len(self._repository.find_by_card(card_number)),
        }
