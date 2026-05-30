import pytest
from datetime import datetime

from domain.entities.reward import Reward


class TestRewardCreation:
    def test_creates_valid_reward(self):
        reward = Reward(
            card_number="4111111111111111",
            points=500,
            cashback=7.50,
            restaurant_code="REST-001",
            original_amount=150.0,
        )
        assert reward.card_number == "4111111111111111"
        assert reward.points == 500
        assert reward.cashback == 7.50
        assert reward.restaurant_code == "REST-001"
        assert reward.original_amount == 150.0
        assert isinstance(reward.created_at, datetime)

    def test_raises_error_for_negative_points(self):
        with pytest.raises(ValueError, match="Points cannot be negative"):
            Reward(
                card_number="12345678",
                points=-1,
                cashback=5.0,
                restaurant_code="REST-001",
                original_amount=100.0,
            )

    def test_raises_error_for_negative_cashback(self):
        with pytest.raises(ValueError, match="Cashback cannot be negative"):
            Reward(
                card_number="12345678",
                points=100,
                cashback=-1.0,
                restaurant_code="REST-001",
                original_amount=100.0,
            )

    def test_raises_error_for_empty_card_number(self):
        with pytest.raises(ValueError, match="Card number cannot be empty"):
            Reward(
                card_number="",
                points=100,
                cashback=5.0,
                restaurant_code="REST-001",
                original_amount=100.0,
            )

    def test_zero_points_is_valid(self):
        reward = Reward(
            card_number="12345678",
            points=0,
            cashback=0.0,
            restaurant_code="REST-001",
            original_amount=100.0,
        )
        assert reward.points == 0
        assert reward.cashback == 0.0


class TestRewardSerialization:
    def setup_method(self):
        self.reward = Reward(
            card_number="4111111111111111",
            points=1550,
            cashback=7.50,
            restaurant_code="REST-001",
            original_amount=150.0,
            created_at=datetime(2026, 5, 16, 12, 0, 0),
        )

    def test_to_dict_has_all_keys(self):
        d = self.reward.to_dict()
        for key in ["card_number", "points", "cashback", "restaurant_code", "original_amount", "created_at"]:
            assert key in d

    def test_from_dict_reconstructs_reward(self):
        d = self.reward.to_dict()
        restored = Reward.from_dict(d)
        assert restored.card_number == self.reward.card_number
        assert restored.points == self.reward.points
        assert restored.cashback == self.reward.cashback
        assert restored.restaurant_code == self.reward.restaurant_code
        assert restored.original_amount == self.reward.original_amount
        assert restored.created_at == self.reward.created_at
