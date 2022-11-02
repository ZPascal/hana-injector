import paho.mqtt.client as mqtt

from converter.converter import Converter
from load_config.config import LoadConfig
from custom_logger.logger import HanaInjectorError


class MQTT:
    """The class includes all necessary methods to establish an connection to the MQTT Broker"""

    _client = mqtt.Client()
    _config = LoadConfig.load_correct_config_dict()

    NO_CONFIG_AVAILABLE_MESSAGE: str = "Can't parse the config yaml. Please, define a valid config yaml"

    def __init__(self):
        if self._config is None:
            raise HanaInjectorError(self.NO_CONFIG_AVAILABLE_MESSAGE) from Exception

        try:
            if (
                self._config["mqtt"]["username"] != ""
                and self._config["mqtt"]["password"] != ""
            ):
                self._client.username_pw_set(
                    self._config["mqtt"]["username"], self._config["mqtt"]["password"]
                )
            else:
                raise HanaInjectorError(
                "Value not available. Please, set the correct "
                "parameter: mqtt.username or mqtt.password",
                ) from KeyError
        except (KeyError, ValueError) as e:
           raise HanaInjectorError(
                "Value not available. Please, set the correct "
                "parameter: mqtt.username or mqtt.password",
           ) from e

        self._client.on_connect = self._mqtt_subscriber_generator

        # Forward the Topic answers to right Method
        self._client.on_message = self._message_callback_generator

        # Connection to the MQTT Broker
        try:
            if (
                self._config["mqtt"]["hostname"] != ""
                and self._config["mqtt"]["port"] != ""
            ):
                self._client.connect(
                    self._config["mqtt"]["hostname"], self._config["mqtt"]["port"], 60
                )
            else:
                raise HanaInjectorError(
                    "Value not available. Please, set the correct parameter: mqtt.hostname or mqtt.port",
                ) from KeyError
        except (KeyError, ValueError) as e:
            raise HanaInjectorError(
                "Value not available. Please, set the correct parameter: mqtt.hostname or mqtt.port",
            ) from e

        self._client.loop_forever()

    @classmethod
    def _mqtt_subscriber_generator(cls):
        """The method includes a functionality to generate the mqtt subscribers

        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace

        Returns:
            None
        """

        if cls._config is None:
            raise HanaInjectorError(cls.NO_CONFIG_AVAILABLE_MESSAGE) from Exception

        try:
            if (
                cls._config["mqtt"]["subscribed_topics"] is not None
                and len(cls._config["mqtt"]["subscribed_topics"]) >= 1
            ):
                for i in range(0, len(cls._config["mqtt"]["subscribed_topics"])):
                    if (
                        cls._config["mqtt"]["subscribed_topics"][i]["name"] != ""
                        or cls._config["mqtt"]["subscribed_topics"][i]["name"]
                        is not None
                    ) and (
                        cls._config["mqtt"]["subscribed_topics"][i]["qos"] != ""
                        or cls._config["mqtt"]["subscribed_topics"][i]["qos"] is not None
                    ):
                        cls._client.subscribe(
                            cls._config["mqtt"]["subscribed_topics"][i]["name"],
                            cls._config["mqtt"]["subscribed_topics"][i]["qos"],
                        )
                    else:
                        raise HanaInjectorError(
                            "Value not available. Please, set the correct "
                            "parameter: mqtt.subscribed_topics. name or qos",
                        ) from ValueError
            else:
                raise HanaInjectorError(
                    "Value not available. Please, set the correct parameter: mqtt.subscribed_topics",
                ) from ValueError
        except (KeyError, ValueError) as e:
            raise HanaInjectorError(
                "Value not available. Please, set the correct parameter: mqtt.subscribed_topics",
            ) from e

    @classmethod
    def _message_callback_generator(cls):
        """The method includes a functionality to handle the mqtt callback

        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace

        Returns:
            None
        """

        if cls._config is None:
            raise HanaInjectorError(cls.NO_CONFIG_AVAILABLE_MESSAGE) from Exception

        try:
            if (
                cls._config["generator"] is not None
                and len(cls._config["generator"]) >= 1
            ):
                for i in range(0, len(cls._config["generator"])):
                    if (
                        (
                            cls._config["generator"][i]["method_name"] != ""
                            or cls._config["generator"][i]["method_name"] is not None
                        )
                        and (
                            cls._config["generator"][i]["mqtt_topic"] != ""
                            or cls._config["generator"][i]["mqtt_topic"] is not None
                        )
                        and (
                            cls._config["generator"][i]["hana_sql_query"] != ""
                            or cls._config["generator"][i]["hana_sql_query"] is not None
                        )
                    ):
                        converter = Converter()
                        cls._client.message_callback_add("Service11", converter.service1)
                        cls._client.message_callback_add("Service21", converter.service2)
                        cls._client.message_callback_add("Service31", converter.service3)
                    else:
                        raise HanaInjectorError(
                            "Value not available. Please, set the correct "
                            "parameter: generator. method_name, mqtt_topic "
                            "or hana_sql_query",
                        ) from ValueError
            else:
                raise HanaInjectorError(
                    "Value not available. Please, set the correct "
                    "parameter: generator",
                ) from ValueError
        except (KeyError, ValueError) as e:
            raise HanaInjectorError(
                "Value not available. Please, set the correct parameter: generator",
            ) from e
