import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application.use_cases.process_reward import ProcessRewardUseCase
from domain.entities.dinner_transaction import DinnerTransaction
from infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from infrastructure.repositories.in_memory_reward_repository import InMemoryRewardRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "213.199.42.57")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "students")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "Ut3c2026")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST", "/")


def main() -> None:
    repository = InMemoryRewardRepository()
    use_case = ProcessRewardUseCase(repository=repository)
    consumer = RabbitMQConsumer(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USER,
        password=RABBITMQ_PASS,
        virtual_host=RABBITMQ_VHOST,
    )

    def on_transaction_received(transaction: DinnerTransaction) -> None:
        reward = use_case.execute(transaction)
        summary = use_case.get_account_summary(transaction.card_number)

        print("\n [x] Reward processed!")
        print(f"     Card      : {reward.card_number}")
        print(f"     Points    : +{reward.points}")
        print(f"     Cashback  : S/ {reward.cashback:.2f}")
        print(f"     Restaurant: {reward.restaurant_code}")
        print("     --- Account Summary ---")
        print(f"     Total Points  : {summary['total_points']}")
        print(f"     Total Cashback: S/ {summary['total_cashback']:.2f}")
        print(f"     Total Rewards : {summary['reward_count']}")

    try:
        print(" [*] Rewards consumer started. Waiting for transactions...")
        print(" [*] Press CTRL+C to stop.\n")
        consumer.start_consuming(callback=on_transaction_received)
    except KeyboardInterrupt:
        print("\n [*] Shutting down consumer...")
    finally:
        consumer.stop()


if __name__ == "__main__":
    main()
