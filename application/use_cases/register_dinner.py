from datetime import datetime, timezone

from application.interfaces.ports import MessagePublisher
from domain.entities.dinner_transaction import DinnerTransaction


class RegisterDinnerUseCase:

    def __init__(self, publisher: MessagePublisher) -> None:
        self._publisher = publisher

    def execute(
        self,
        amount: float,
        card_number: str,
        restaurant_code: str,
        transaction_date: datetime = None,
    ) -> DinnerTransaction:
        transaction = DinnerTransaction(
            amount=amount,
            card_number=card_number,
            restaurant_code=restaurant_code,
            transaction_date=transaction_date or datetime.now(timezone.utc),
        )

        self._publisher.publish(transaction)
        return transaction
