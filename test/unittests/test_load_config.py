import os
from typing import Dict
from unittest import TestCase

from load_config.load_config import LoadConfig


def _get_template_path() -> str:
    if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
        return f"{os.getcwd()}"
    else:
        return "../.."


class LoadConfigCase(TestCase):
    maxDiff = None

    mocked_config_dict: Dict = {
        "hana_injector": {
            "secret_key": "test",
            "log_mode": "debug",
            "template": f"{ _get_template_path() }/injector/templates",
            "host": "localhost",
            "port": 8080,
            "threads": 4
        },
        "mqtt": {
            "hostname": "localhost",
            "port": 3555,
            "username": "3555",
            "password": "3555",
            "subscribed_topics": [
                {"name": "Test1", "qos": 0},
                {"name": "Test2", "qos": 0},
            ],
        },
        "hana_database": {
            "hostname": "Test",
            "port": 123,
            "username": "test",
            "password": "Test",
        },
        "generator": [
            {
                "method_name": "Service1",
                "mqtt_topic": "Service11",
                "mqtt_payload": [
                    {"OrderID": "str"},
                    {"OrderDate": "generateDatetime"},
                    {"Color": "sep:ListDict(Name, Amount)|OrderID, OrderDate"},
                    {"Color2": "sep:ListDict(Name, Amount)|OrderID, OrderDate"},
                    {"CustomerName": "str"},
                ],
                "hana_sql_query": ["Test1"],
                "hana_sql_query_sep": ["Test1_sep", "Test2_sep"],
            },
            {
                "method_name": "Service2",
                "mqtt_topic": "Service21",
                "mqtt_payload": [
                    {"OrderID": "str"},
                    {"OrderDate": "generateDate"},
                    {"CustomerName": "str"},
                    {"Color": "List"},
                ],
                "hana_sql_query": ["Test2", "Test22"],
            },
            {
                "method_name": "Service3",
                "mqtt_topic": "Service31",
                "mqtt_payload": [
                    {"OrderID": "str"},
                    {"DeviceID": "str"},
                    {"OrderDate": "str"},
                    {"StatusCode": "str"},
                ],
                "hana_sql_query": ["Test3"],
            },
        ],
    }

    def test_load_correct_config_dict_env_variable_successful(self):
        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = os.environ.get(
                "HANA_INJECTOR_CONFIG_FILE_PATH_2"
            )
            self.assertEqual(
                os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"],
                os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2"),
            )
        else:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = "config/config.yml"
            self.assertEqual(
                os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"], "config/config.yml"
            )

    def test_load_correct_config_dict_env_variable_error(self):
        # Variable should be removed to test the KeyError
        del os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"]
        with self.assertRaises(KeyError) as raises:
            LoadConfig.load_correct_config_dict()
        self.assertEqual(
            str(raises.exception),
            str(
                KeyError("Please, set the HANA_INJECTOR_CONFIG_FILE_PATH env variable.")
            ),
        )

    def test_load_correct_config_dict_get_config_successful(self):
        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = os.environ.get(
                "HANA_INJECTOR_CONFIG_FILE_PATH_2"
            )
        else:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = "config/config.yml"
        self.assertEqual(self.mocked_config_dict, LoadConfig.load_correct_config_dict())

    def test_load_correct_config_get_config_dict_error(self):
        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = os.environ.get(
                "HANA_INJECTOR_CONFIG_FILE_PATH_2"
            )
        else:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = "config/config.yml"
        config: Dict = LoadConfig.load_correct_config_dict()
        config["hana_injector"] = "test"
        self.assertNotEqual(config, self.mocked_config_dict)
