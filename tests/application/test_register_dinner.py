import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, call

from application.use_cases.register_dinner import RegisterDinnerUseCase
from application.interfaces.ports import MessagePublisher
from domain.entities.dinner_transaction import DinnerTransaction


class TestRegisterDinnerUseCase:
    def setup_method(self):
        self.mock_publisher = MagicMock(spec=MessagePublisher)
        self.use_case = RegisterDinnerUseCase(publisher=self.mock_publisher)

    def test_execute_returns_dinner_transaction(self):
        result = self.use_case.execute(
            amount=100.0,
            card_number="4111111111111111",
            restaurant_code="REST-001",
        )
        assert isinstance(result, DinnerTransaction)

    def test_execute_calls_publisher_once(self):
        self.use_case.execute(
            amount=100.0,
            card_number="4111111111111111",
            restaurant_code="REST-001",
        )
        self.mock_publisher.publish.assert_called_once()

    def test_execute_publishes_correct_transaction(self):
        date = datetime(2026, 5, 16, 10, 0, 0)
        result = self.use_case.execute(
            amount=250.0,
            card_number="87654321",
            restaurant_code="REST-XYZ",
            transaction_date=date,
        )
        published = self.mock_publisher.publish.call_args[0][0]
        assert published.amount == 250.0
        assert published.card_number == "87654321"
        assert published.restaurant_code == "REST-XYZ"
        assert published.transaction_date == date

    def test_execute_uses_current_date_when_none_provided(self):
        before = datetime.now(timezone.utc)
        result = self.use_case.execute(
            amount=50.0,
            card_number="12345678",
            restaurant_code="REST-002",
        )
        after = datetime.now(timezone.utc)
        assert before <= result.transaction_date <= after

    def test_execute_raises_for_invalid_amount(self):
        with pytest.raises(ValueError):
            self.use_case.execute(
                amount=0,
                card_number="12345678",
                restaurant_code="REST-001",
            )
        self.mock_publisher.publish.assert_not_called()

    def test_execute_raises_for_short_card_number(self):
        with pytest.raises(ValueError):
            self.use_case.execute(
                amount=50.0,
                card_number="123",
                restaurant_code="REST-001",
            )

    def test_execute_raises_for_empty_card_number(self):
        with pytest.raises(ValueError):
            self.use_case.execute(
                amount=50.0,
                card_number="",
                restaurant_code="REST-001",
            )

    def test_multiple_executions_call_publisher_multiple_times(self):
        self.use_case.execute(100.0, "12345678", "REST-001")
        self.use_case.execute(200.0, "12345678", "REST-002")
        assert self.mock_publisher.publish.call_count == 2
