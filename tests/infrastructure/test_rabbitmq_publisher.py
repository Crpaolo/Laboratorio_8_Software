import json
from datetime import datetime
from unittest.mock import MagicMock, patch

from infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher
from domain.entities.dinner_transaction import DinnerTransaction


def make_publisher(mock_pika):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_pika.BlockingConnection.return_value = mock_connection
    publisher = RabbitMQPublisher(
        host="localhost",
        port=5672,
        username="user",
        password="pass",
    )
    return publisher, mock_connection, mock_channel


def make_transaction():
    return DinnerTransaction(
        amount=150.0,
        card_number="4111111111111111",
        restaurant_code="REST-001",
        transaction_date=datetime(2026, 5, 16, 12, 0, 0),
    )


class TestRabbitMQPublisherInit:
    def test_creates_blocking_connection(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            make_publisher(mock_pika)
            mock_pika.BlockingConnection.assert_called_once()

    def test_declares_durable_queue_on_init(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            _, _, mock_channel = make_publisher(mock_pika)
            mock_channel.queue_declare.assert_called_once_with(
                queue="rewards_transactions", durable=True
            )

    def test_creates_credentials_with_provided_user_and_pass(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            make_publisher(mock_pika)
            mock_pika.PlainCredentials.assert_called_once_with("user", "pass")


class TestRabbitMQPublisherPublish:
    def test_publish_calls_basic_publish_once(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            publisher, _, mock_channel = make_publisher(mock_pika)
            publisher.publish(make_transaction())
            mock_channel.basic_publish.assert_called_once()

    def test_publish_sends_correct_json_body(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            publisher, _, mock_channel = make_publisher(mock_pika)
            tx = make_transaction()
            publisher.publish(tx)
            body = json.loads(mock_channel.basic_publish.call_args[1]["body"])
            assert body["amount"] == 150.0
            assert body["card_number"] == "4111111111111111"
            assert body["restaurant_code"] == "REST-001"

    def test_publish_routes_to_correct_queue(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            publisher, _, mock_channel = make_publisher(mock_pika)
            publisher.publish(make_transaction())
            assert mock_channel.basic_publish.call_args[1]["routing_key"] == "rewards_transactions"

    def test_publish_uses_persistent_delivery_mode(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            publisher, _, _ = make_publisher(mock_pika)
            publisher.publish(make_transaction())
            mock_pika.BasicProperties.assert_called_once_with(
                delivery_mode=2,
                content_type="application/json",
            )


class TestRabbitMQPublisherClose:
    def test_close_calls_connection_close_when_open(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            publisher, mock_connection, _ = make_publisher(mock_pika)
            mock_connection.is_open = True
            publisher.close()
            mock_connection.close.assert_called_once()

    def test_close_does_not_call_close_when_already_closed(self):
        with patch("infrastructure.messaging.rabbitmq_publisher.pika") as mock_pika:
            publisher, mock_connection, _ = make_publisher(mock_pika)
            mock_connection.is_open = False
            publisher.close()
            mock_connection.close.assert_not_called()
