import json
import logging
from typing import Callable

import pika

from application.interfaces.ports import MessageConsumer
from domain.entities.dinner_transaction import DinnerTransaction

logger = logging.getLogger(__name__)

QUEUE_NAME = "rewards_transactions"


class RabbitMQConsumer(MessageConsumer):

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
        self._parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=credentials,
        )
        self._connection = None
        self._channel = None

    def start_consuming(self, callback: Callable[[DinnerTransaction], None]) -> None:
        self._connection = pika.BlockingConnection(self._parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self._queue_name, durable=True)
        self._channel.basic_qos(prefetch_count=1)

        def _on_message(ch, method, properties, body):
            try:
                data = json.loads(body.decode("utf-8"))
                transaction = DinnerTransaction.from_dict(data)
                callback(transaction)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(
                    "Consumed message: card=%s amount=%.2f",
                    transaction.card_number,
                    transaction.amount,
                )
            except (KeyError, ValueError) as exc:
                logger.error("Failed to process message: %s", exc)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self._channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=_on_message,
        )
        logger.info("Waiting for messages in '%s'. Press CTRL+C to stop.", self._queue_name)
        self._channel.start_consuming()

    def stop(self) -> None:
        if self._channel and self._channel.is_open:
            self._channel.stop_consuming()
        if self._connection and self._connection.is_open:
            self._connection.close()
        logger.info("RabbitMQConsumer stopped.")
