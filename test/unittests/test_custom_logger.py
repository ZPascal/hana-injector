import logging
from typing import Dict

from unittest import TestCase
from unittest.mock import patch, MagicMock

from load_config.config import LoadConfig
from custom_logger.logger import HanaInjectorError


class CustomLoggerCase(TestCase):
    name = "hana_injector"

    def test_get_logger_successful_non_exist_logger(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(
            str(CustomLogger._get_logger(self.name)),
            str("<Logger hana_injector (DEBUG)>"),
        )

    def test_get_logger_successful_exist_logger(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(
            str(CustomLogger._get_logger(self.name)),
            str("<Logger hana_injector (DEBUG)>"),
        )

    def test_get_logger_error(self):
        from custom_logger.logger import CustomLogger

        self.assertNotEqual(
            str(CustomLogger._get_logger("Test")), str("<Logger hana_injector (DEBUG)>")
        )

    def test_write_to_console_successful(self):
        from custom_logger.logger import CustomLogger

        CustomLogger.config = LoadConfig.load_correct_config_dict()
        self.assertEqual(CustomLogger.write_to_console("error", "test"), None)

    def test_get_logger_no_config(self):
        from custom_logger.logger import CustomLogger

        with self.assertRaises(HanaInjectorError):
            CustomLogger.config = None
            CustomLogger.write_to_console("", "")

    def test_write_to_console_error_mode(self):
        from custom_logger.logger import CustomLogger

        config: Dict = LoadConfig.load_correct_config_dict()
        config["hana_injector"]["log_mode"] = "info"
        CustomLogger.config = config
        self.assertEqual(CustomLogger.write_to_console("error", "test"), None)

    def test_write_to_console_info_mode(self):
        from custom_logger.logger import CustomLogger

        config: Dict = LoadConfig.load_correct_config_dict()
        config["hana_injector"]["log_mode"] = "info"
        CustomLogger.config = config
        self.assertEqual(CustomLogger.write_to_console("info", "test"), None)

    def test_write_to_console_no_log_mode(self):
        from custom_logger.logger import CustomLogger

        config: Dict = LoadConfig.load_correct_config_dict()
        del config["hana_injector"]["log_mode"]
        CustomLogger.config = config

        with self.assertRaises(ValueError):
            CustomLogger.write_to_console("error", "test")

    def test_get_correct_status_successful(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(
            CustomLogger._get_correct_status(
                CustomLogger._get_logger("hana_injector"), "error", "Test"
            ),
            None,
        )

    def test_get_correct_status_warning(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(
            CustomLogger._get_correct_status(
                CustomLogger._get_logger("hana_injector"), "warning", "Test"
            ),
            None,
        )

    def test_get_correct_status_test(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(
            CustomLogger._get_correct_status(
                CustomLogger._get_logger("hana_injector"), "test", "Test"
            ),
            None,
        )

    def test_get_log_level_parameter_successful(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(CustomLogger._get_log_level_parameter("debug"), logging.DEBUG)

    def test_get_log_level_parameter_test(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(CustomLogger._get_log_level_parameter("test"), logging.DEBUG)

    def test_get_log_level_parameter_warning(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(
            CustomLogger._get_log_level_parameter("warning"), logging.WARNING
        )

    def test_get_log_level_parameter_error(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(CustomLogger._get_log_level_parameter("error"), logging.ERROR)

    def test_get_log_level_parameter_information(self):
        from custom_logger.logger import CustomLogger

        self.assertEqual(
            CustomLogger._get_log_level_parameter("information"), logging.INFO
        )
