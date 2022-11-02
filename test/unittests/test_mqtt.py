from unittest import TestCase
from unittest.mock import patch, MagicMock

from custom_logger.logger import HanaInjectorError


class MQTTTestCase(TestCase):
    @patch("broker_mqtt.mqtt.MQTT._config", MagicMock(None))
    def test_mqtt_subscriber_generator_general_issue(self):
        with self.assertRaises(HanaInjectorError) as raises:
            from broker_mqtt.mqtt import MQTT

            MQTT._mqtt_subscriber_generator()
        self.assertEqual(
            str(raises.exception),
            str(
                "Value not available. Please, set the correct parameter: mqtt.subscribed_topics"
            ),
        )

    @patch("broker_mqtt.mqtt.MQTT._config", MagicMock(None))
    def test_mqtt_subscriber_generator_no_config_error(self):
        with self.assertRaises(HanaInjectorError):
            from broker_mqtt.mqtt import MQTT

            MQTT._config = None
            MQTT._mqtt_subscriber_generator()

    def test_mqtt_subscriber_generator_subscribed_topics_empty_name(self):
        with self.assertRaises(HanaInjectorError):
            from broker_mqtt.mqtt import MQTT

            MQTT._config = dict({"mqtt": {"subscribed_topics": [{"name": ""}]}})
            MQTT._mqtt_subscriber_generator()

    def test_mqtt_subscriber_generator(self):
        from broker_mqtt.mqtt import MQTT

        MQTT._client.subscribe = MagicMock()
        MQTT._config = dict(
            {"mqtt": {"subscribed_topics": [{"name": "test", "qos": 1}]}}
        )
        self.assertEqual(MQTT._mqtt_subscriber_generator(), None)

    def test_mqtt_no_config_error(self):
        with self.assertRaises(HanaInjectorError):
            from broker_mqtt.mqtt import MQTT

            MQTT._config = None
            MQTT()

    def test_mqtt_no_credentials_error(self):
        with self.assertRaises(HanaInjectorError):
            from broker_mqtt.mqtt import MQTT

            MQTT._config = dict({"mqtt": {"username": ""}})
            MQTT()

    def test_mqtt_credentials_none_error(self):
        with self.assertRaises(HanaInjectorError):
            from broker_mqtt.mqtt import MQTT

            MQTT._config = dict({"mqtt": {}})
            MQTT()

    def test_mqtt(self):
        from broker_mqtt.mqtt import MQTT

        MQTT._client.connect = MagicMock()
        MQTT._client.loop_forever = MagicMock()

        self.assertIn("<broker_mqtt.mqtt.MQTT", str(MQTT()))

    def test_mqtt_no_hostname(self):
        from broker_mqtt.mqtt import MQTT

        MQTT._config = dict({})

        with self.assertRaises(HanaInjectorError):
            MQTT._config = dict(
                {
                    "mqtt": {
                        "username": "test",
                        "password": "test",
                        "hostname": "",
                        "port": 3555,
                    }
                }
            )
            MQTT()

    def test_mqtt_no_port(self):
        from broker_mqtt.mqtt import MQTT

        MQTT._config = dict({})

        with self.assertRaises(HanaInjectorError):
            MQTT._config = dict({"mqtt": {"username": "test", "password": "test"}})
            MQTT()

    @patch("broker_mqtt.mqtt.MQTT._config", MagicMock(None))
    def test_message_callback_generator_no_generator(self):
        with self.assertRaises(HanaInjectorError):
            from broker_mqtt.mqtt import MQTT

            MQTT._config = dict({})
            MQTT._message_callback_generator()

    @patch("broker_mqtt.mqtt.MQTT._config", MagicMock(None))
    def test_message_callback_generator_no_generator_value(self):
        with self.assertRaises(HanaInjectorError) as raises:
            from broker_mqtt.mqtt import MQTT

            MQTT._message_callback_generator()
        self.assertEqual(
            str(raises.exception),
            str("Value not available. Please, set the correct parameter: generator"),
        )

    @patch("broker_mqtt.mqtt.MQTT._config", MagicMock(None))
    def test_message_callback_generator_no_config_error(self):
        with self.assertRaises(HanaInjectorError):
            from broker_mqtt.mqtt import MQTT

            MQTT._config = None
            MQTT._message_callback_generator()

    @patch("broker_mqtt.mqtt.MQTT._config", MagicMock(None))
    @patch("converter.converter.Converter")
    def test_message_callback_generator(self, converter_mock):
        from broker_mqtt.mqtt import MQTT

        MQTT._config = dict(
            {
                "generator": [
                    {
                        "method_name": "test",
                        "mqtt_topic": "test",
                        "hana_sql_query": "test",
                    }
                ]
            }
        )
        MQTT._message_callback_generator()
