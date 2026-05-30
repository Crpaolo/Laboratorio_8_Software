import pytest

from domain.value_objects.reward_calculation import (
    RewardCalculation,
    POINTS_PER_UNIT,
    CASHBACK_RATE,
    MIN_AMOUNT_FOR_BONUS,
    BONUS_POINTS,
)


class TestRewardCalculationBasic:
    def test_calculates_points_correctly(self):
        calc = RewardCalculation.from_amount(10.0)
        assert calc.points == int(10.0 * POINTS_PER_UNIT)

    def test_calculates_cashback_correctly(self):
        calc = RewardCalculation.from_amount(200.0)
        assert calc.cashback == round(200.0 * CASHBACK_RATE, 2)

    def test_small_amount_no_bonus(self):
        amount = MIN_AMOUNT_FOR_BONUS - 0.01
        calc = RewardCalculation.from_amount(amount)
        expected_points = int(amount * POINTS_PER_UNIT)
        assert calc.points == expected_points

    def test_exact_threshold_gets_bonus(self):
        calc = RewardCalculation.from_amount(MIN_AMOUNT_FOR_BONUS)
        expected_points = int(MIN_AMOUNT_FOR_BONUS * POINTS_PER_UNIT) + BONUS_POINTS
        assert calc.points == expected_points

    def test_large_amount_gets_bonus(self):
        calc = RewardCalculation.from_amount(500.0)
        expected_points = int(500.0 * POINTS_PER_UNIT) + BONUS_POINTS
        assert calc.points == expected_points

    def test_raises_for_zero_amount(self):
        with pytest.raises(ValueError, match="Amount must be greater than zero"):
            RewardCalculation.from_amount(0)

    def test_raises_for_negative_amount(self):
        with pytest.raises(ValueError, match="Amount must be greater than zero"):
            RewardCalculation.from_amount(-50.0)

    def test_is_frozen(self):
        calc = RewardCalculation.from_amount(50.0)
        with pytest.raises(Exception):
            calc.points = 9999

    def test_cashback_is_rounded_to_two_decimals(self):
        calc = RewardCalculation.from_amount(33.33)
        assert calc.cashback == round(33.33 * CASHBACK_RATE, 2)

    def test_fractional_amount(self):
        calc = RewardCalculation.from_amount(1.5)
        assert calc.points == int(1.5 * POINTS_PER_UNIT)
        assert calc.cashback == round(1.5 * CASHBACK_RATE, 2)
