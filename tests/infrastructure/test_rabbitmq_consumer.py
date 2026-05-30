import json
from unittest.mock import MagicMock, patch

from infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from domain.entities.dinner_transaction import DinnerTransaction


def make_consumer(mock_pika):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_pika.BlockingConnection.return_value = mock_connection
    consumer = RabbitMQConsumer(
        host="localhost",
        port=5672,
        username="user",
        password="pass",
    )
    return consumer, mock_connection, mock_channel


def valid_body():
    return json.dumps({
        "amount": 100.0,
        "card_number": "12345678",
        "restaurant_code": "REST-001",
        "transaction_date": "2026-05-16T12:00:00",
    }).encode("utf-8")


def get_on_message(mock_pika, callback=None):
    consumer, _, mock_channel = make_consumer(mock_pika)
    consumer.start_consuming(callback or (lambda tx: None))
    return mock_channel.basic_consume.call_args[1]["on_message_callback"]


class TestRabbitMQConsumerStartConsuming:
    def test_creates_blocking_connection(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            consumer, _, _ = make_consumer(mock_pika)
            consumer.start_consuming(lambda tx: None)
            mock_pika.BlockingConnection.assert_called_once()

    def test_declares_durable_queue(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            consumer, _, mock_channel = make_consumer(mock_pika)
            consumer.start_consuming(lambda tx: None)
            mock_channel.queue_declare.assert_called_once_with(
                queue="rewards_transactions", durable=True
            )

    def test_sets_qos_prefetch_count(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            consumer, _, mock_channel = make_consumer(mock_pika)
            consumer.start_consuming(lambda tx: None)
            mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)

    def test_registers_message_callback(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            consumer, _, mock_channel = make_consumer(mock_pika)
            consumer.start_consuming(lambda tx: None)
            mock_channel.basic_consume.assert_called_once()

    def test_calls_start_consuming_on_channel(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            consumer, _, mock_channel = make_consumer(mock_pika)
            consumer.start_consuming(lambda tx: None)
            mock_channel.start_consuming.assert_called_once()


class TestRabbitMQConsumerOnMessage:
    def test_callback_receives_dinner_transaction(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            received = []
            on_message = get_on_message(mock_pika, received.append)
            on_message(MagicMock(), MagicMock(), MagicMock(), valid_body())
            assert len(received) == 1
            assert isinstance(received[0], DinnerTransaction)

    def test_callback_receives_correct_transaction_data(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            received = []
            on_message = get_on_message(mock_pika, received.append)
            on_message(MagicMock(), MagicMock(), MagicMock(), valid_body())
            assert received[0].amount == 100.0
            assert received[0].card_number == "12345678"
            assert received[0].restaurant_code == "REST-001"

    def test_ack_sent_on_successful_message(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            on_message = get_on_message(mock_pika)
            mock_ch = MagicMock()
            mock_method = MagicMock()
            on_message(mock_ch, mock_method, MagicMock(), valid_body())
            mock_ch.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)

    def test_nack_sent_on_invalid_json(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            on_message = get_on_message(mock_pika)
            mock_ch = MagicMock()
            mock_method = MagicMock()
            on_message(mock_ch, mock_method, MagicMock(), b"not valid json {{")
            mock_ch.basic_nack.assert_called_once_with(
                delivery_tag=mock_method.delivery_tag, requeue=False
            )

    def test_nack_sent_on_missing_field(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            on_message = get_on_message(mock_pika)
            mock_ch = MagicMock()
            mock_method = MagicMock()
            incomplete = json.dumps({"amount": 100.0}).encode("utf-8")
            on_message(mock_ch, mock_method, MagicMock(), incomplete)
            mock_ch.basic_nack.assert_called_once_with(
                delivery_tag=mock_method.delivery_tag, requeue=False
            )

    def test_ack_not_sent_on_error(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            on_message = get_on_message(mock_pika)
            mock_ch = MagicMock()
            on_message(mock_ch, MagicMock(), MagicMock(), b"bad json")
            mock_ch.basic_ack.assert_not_called()


class TestRabbitMQConsumerStop:
    def test_stop_closes_channel_and_connection(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            consumer, mock_connection, mock_channel = make_consumer(mock_pika)
            consumer.start_consuming(lambda tx: None)
            mock_channel.is_open = True
            mock_connection.is_open = True
            consumer.stop()
            mock_channel.stop_consuming.assert_called_once()
            mock_connection.close.assert_called_once()

    def test_stop_before_connecting_does_not_raise(self):
        with patch("infrastructure.messaging.rabbitmq_consumer.pika") as mock_pika:
            consumer, _, _ = make_consumer(mock_pika)
            consumer.stop()
