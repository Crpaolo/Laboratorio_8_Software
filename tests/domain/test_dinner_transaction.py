import pytest
from datetime import datetime

from domain.entities.dinner_transaction import DinnerTransaction


class TestDinnerTransactionCreation:
    def test_creates_valid_transaction(self):
        tx = DinnerTransaction(
            amount=100.0,
            card_number="4111111111111111",
            restaurant_code="REST-001",
        )
        assert tx.amount == 100.0
        assert tx.card_number == "4111111111111111"
        assert tx.restaurant_code == "REST-001"
        assert isinstance(tx.transaction_date, datetime)

    def test_creates_transaction_with_custom_date(self):
        date = datetime(2026, 5, 16, 12, 0, 0)
        tx = DinnerTransaction(
            amount=50.0,
            card_number="12345678",
            restaurant_code="REST-002",
            transaction_date=date,
        )
        assert tx.transaction_date == date

    def test_raises_error_for_zero_amount(self):
        with pytest.raises(ValueError, match="Amount must be greater than zero"):
            DinnerTransaction(amount=0, card_number="12345678", restaurant_code="REST-001")

    def test_raises_error_for_negative_amount(self):
        with pytest.raises(ValueError, match="Amount must be greater than zero"):
            DinnerTransaction(amount=-10.0, card_number="12345678", restaurant_code="REST-001")

    def test_raises_error_for_short_card_number(self):
        with pytest.raises(ValueError, match="Card number must have at least 8 characters"):
            DinnerTransaction(amount=50.0, card_number="123", restaurant_code="REST-001")

    def test_raises_error_for_empty_card_number(self):
        with pytest.raises(ValueError, match="Card number must have at least 8 characters"):
            DinnerTransaction(amount=50.0, card_number="", restaurant_code="REST-001")

    def test_raises_error_for_empty_restaurant_code(self):
        with pytest.raises(ValueError, match="Restaurant code cannot be empty"):
            DinnerTransaction(amount=50.0, card_number="12345678", restaurant_code="")


class TestDinnerTransactionSerialization:
    def setup_method(self):
        self.tx = DinnerTransaction(
            amount=200.0,
            card_number="4111111111111111",
            restaurant_code="REST-003",
            transaction_date=datetime(2026, 5, 16, 10, 30, 0),
        )

    def test_to_dict_returns_correct_keys(self):
        d = self.tx.to_dict()
        assert "amount" in d
        assert "card_number" in d
        assert "restaurant_code" in d
        assert "transaction_date" in d

    def test_to_dict_values_are_correct(self):
        d = self.tx.to_dict()
        assert d["amount"] == 200.0
        assert d["card_number"] == "4111111111111111"
        assert d["restaurant_code"] == "REST-003"

    def test_from_dict_reconstructs_entity(self):
        d = self.tx.to_dict()
        reconstructed = DinnerTransaction.from_dict(d)
        assert reconstructed.amount == self.tx.amount
        assert reconstructed.card_number == self.tx.card_number
        assert reconstructed.restaurant_code == self.tx.restaurant_code
        assert reconstructed.transaction_date == self.tx.transaction_date

    def test_roundtrip_serialization(self):
        original = DinnerTransaction(
            amount=75.5,
            card_number="87654321",
            restaurant_code="REST-XYZ",
        )
        restored = DinnerTransaction.from_dict(original.to_dict())
        assert original.amount == restored.amount
        assert original.card_number == restored.card_number
        assert original.restaurant_code == restored.restaurant_code
