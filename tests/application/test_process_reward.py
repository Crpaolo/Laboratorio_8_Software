import pytest
from datetime import datetime

from application.use_cases.process_reward import ProcessRewardUseCase
from domain.entities.dinner_transaction import DinnerTransaction
from domain.entities.reward import Reward
from domain.value_objects.reward_calculation import CASHBACK_RATE, POINTS_PER_UNIT, BONUS_POINTS, MIN_AMOUNT_FOR_BONUS
from infrastructure.repositories.in_memory_reward_repository import InMemoryRewardRepository


def make_transaction(amount=100.0, card="4111111111111111", restaurant="REST-001"):
    return DinnerTransaction(
        amount=amount,
        card_number=card,
        restaurant_code=restaurant,
        transaction_date=datetime(2026, 5, 16, 12, 0, 0),
    )


class TestProcessRewardUseCase:
    def setup_method(self):
        self.repository = InMemoryRewardRepository()
        self.use_case = ProcessRewardUseCase(repository=self.repository)

    def test_execute_returns_reward(self):
        tx = make_transaction()
        result = self.use_case.execute(tx)
        assert isinstance(result, Reward)

    def test_execute_stores_reward(self):
        tx = make_transaction()
        self.use_case.execute(tx)
        stored = self.repository.find_by_card("4111111111111111")
        assert len(stored) == 1

    def test_execute_calculates_correct_points(self):
        tx = make_transaction(amount=50.0)
        reward = self.use_case.execute(tx)
        expected = int(50.0 * POINTS_PER_UNIT)
        assert reward.points == expected

    def test_execute_calculates_bonus_points_for_large_amount(self):
        tx = make_transaction(amount=MIN_AMOUNT_FOR_BONUS)
        reward = self.use_case.execute(tx)
        expected = int(MIN_AMOUNT_FOR_BONUS * POINTS_PER_UNIT) + BONUS_POINTS
        assert reward.points == expected

    def test_execute_calculates_correct_cashback(self):
        tx = make_transaction(amount=200.0)
        reward = self.use_case.execute(tx)
        assert reward.cashback == round(200.0 * CASHBACK_RATE, 2)

    def test_execute_assigns_correct_card_number(self):
        tx = make_transaction(card="99999999")
        reward = self.use_case.execute(tx)
        assert reward.card_number == "99999999"

    def test_execute_assigns_correct_restaurant(self):
        tx = make_transaction(restaurant="REST-XYZ")
        reward = self.use_case.execute(tx)
        assert reward.restaurant_code == "REST-XYZ"

    def test_execute_preserves_original_amount(self):
        tx = make_transaction(amount=333.33)
        reward = self.use_case.execute(tx)
        assert reward.original_amount == 333.33


class TestGetAccountSummary:
    def setup_method(self):
        self.repository = InMemoryRewardRepository()
        self.use_case = ProcessRewardUseCase(repository=self.repository)

    def test_summary_with_no_rewards(self):
        summary = self.use_case.get_account_summary("0000000000000000")
        assert summary["total_points"] == 0
        assert summary["total_cashback"] == 0.0
        assert summary["reward_count"] == 0

    def test_summary_accumulates_multiple_rewards(self):
        self.use_case.execute(make_transaction(amount=50.0))
        self.use_case.execute(make_transaction(amount=50.0))
        summary = self.use_case.get_account_summary("4111111111111111")
        assert summary["reward_count"] == 2
        assert summary["total_points"] > 0
        assert summary["total_cashback"] > 0

    def test_summary_is_card_specific(self):
        self.use_case.execute(make_transaction(card="CARD-AAA"))
        self.use_case.execute(make_transaction(card="CARD-BBB"))
        summary_a = self.use_case.get_account_summary("CARD-AAA")
        summary_b = self.use_case.get_account_summary("CARD-BBB")
        assert summary_a["reward_count"] == 1
        assert summary_b["reward_count"] == 1
