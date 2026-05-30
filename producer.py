import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application.use_cases.register_dinner import RegisterDinnerUseCase
from infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher

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
    publisher = None
    try:
        publisher = RabbitMQPublisher(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            username=RABBITMQ_USER,
            password=RABBITMQ_PASS,
            virtual_host=RABBITMQ_VHOST,
        )

        use_case = RegisterDinnerUseCase(publisher=publisher)

        transaction = use_case.execute(
            amount=150.00,
            card_number="4111111111111111",
            restaurant_code="REST-001",
        )

        print("\n [x] Dinner registered successfully!")
        print(f"     Card    : {transaction.card_number}")
        print(f"     Amount  : S/ {transaction.amount:.2f}")
        print(f"     Rest.   : {transaction.restaurant_code}")
        print(f"     Date    : {transaction.transaction_date.isoformat()}")

    except Exception as exc:
        logging.error("Producer error: %s", exc)
        sys.exit(1)
    finally:
        if publisher:
            publisher.close()


if __name__ == "__main__":
    main()
