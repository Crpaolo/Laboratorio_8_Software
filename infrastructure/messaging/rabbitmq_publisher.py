import json
import logging

import pika

from application.interfaces.ports import MessagePublisher
from domain.entities.dinner_transaction import DinnerTransaction

logger = logging.getLogger(__name__)

QUEUE_NAME = "rewards_transactions"
EXCHANGE = ""


class RabbitMQPublisher(MessagePublisher):

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        virtual_host: str = "/",
        queue_name: str = QUEUE_NAME,
    ) -> None:
        self._queue_name = queue_name
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=credentials,
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self._queue_name, durable=True)
        logger.info("RabbitMQPublisher connected. Queue: %s", self._queue_name)

    def publish(self, transaction: DinnerTransaction) -> None:
        body = json.dumps(transaction.to_dict())
        self._channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=self._queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
        logger.info(
            "Published transaction: card=%s restaurant=%s amount=%.2f",
            transaction.card_number,
            transaction.restaurant_code,
            transaction.amount,
        )

    def close(self) -> None:
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("RabbitMQPublisher connection closed.")
