import pytest
from datetime import datetime

from infrastructure.repositories.in_memory_reward_repository import InMemoryRewardRepository
from domain.entities.reward import Reward


def make_reward(card="4111111111111111", points=500, cashback=7.5, restaurant="REST-001", amount=150.0):
    return Reward(
        card_number=card,
        points=points,
        cashback=cashback,
        restaurant_code=restaurant,
        original_amount=amount,
        created_at=datetime(2026, 5, 16, 12, 0, 0),
    )


class TestInMemoryRewardRepository:
    def setup_method(self):
        self.repo = InMemoryRewardRepository()

    def test_save_stores_reward(self):
        reward = make_reward()
        self.repo.save(reward)
        assert len(self.repo.find_all()) == 1

    def test_find_all_returns_empty_initially(self):
        assert self.repo.find_all() == []

    def test_find_by_card_returns_matching_rewards(self):
        self.repo.save(make_reward(card="CARD-A"))
        self.repo.save(make_reward(card="CARD-B"))
        results = self.repo.find_by_card("CARD-A")
        assert len(results) == 1
        assert results[0].card_number == "CARD-A"

    def test_find_by_card_returns_empty_for_unknown_card(self):
        assert self.repo.find_by_card("UNKNOWN") == []

    def test_total_points_sums_correctly(self):
        self.repo.save(make_reward(card="CARD-A", points=100))
        self.repo.save(make_reward(card="CARD-A", points=200))
        self.repo.save(make_reward(card="CARD-B", points=999))
        assert self.repo.total_points("CARD-A") == 300

    def test_total_cashback_sums_correctly(self):
        self.repo.save(make_reward(card="CARD-A", cashback=5.0))
        self.repo.save(make_reward(card="CARD-A", cashback=3.25))
        assert self.repo.total_cashback("CARD-A") == 8.25

    def test_total_points_for_unknown_card_is_zero(self):
        assert self.repo.total_points("NOBODY") == 0

    def test_total_cashback_for_unknown_card_is_zero(self):
        assert self.repo.total_cashback("NOBODY") == 0.0

    def test_clear_removes_all_records(self):
        self.repo.save(make_reward())
        self.repo.save(make_reward())
        self.repo.clear()
        assert self.repo.find_all() == []

    def test_multiple_cards_are_independent(self):
        self.repo.save(make_reward(card="CARD-A", points=100))
        self.repo.save(make_reward(card="CARD-B", points=200))
        assert self.repo.total_points("CARD-A") == 100
        assert self.repo.total_points("CARD-B") == 200

    def test_find_all_returns_all_rewards(self):
        self.repo.save(make_reward(card="CARD-A"))
        self.repo.save(make_reward(card="CARD-B"))
        self.repo.save(make_reward(card="CARD-C"))
        assert len(self.repo.find_all()) == 3
