"""
Created on 18.02.2020

@author: Pascal Zimmermann
"""

import logging
from jsonformatter import JsonFormatter
from typing import Dict

from load_config.load_config import LoadConfig


class HanaInjectorError(Exception):
    pass


class CustomLogger:
    """
    Logger class
    """

    loggers: Dict = dict()

    log_format: str = """{
        "Name":            "name",
        "Levelno":         "levelno",
        "Levelname":       "levelname",
        "Pathname":        "pathname",
        "Filename":        "filename",
        "Module":          "module",
        "Lineno":          "lineno",
        "FuncName":        "funcName",
        "Created":         "created",
        "Asctime":         "asctime",
        "Msecs":           "msecs",
        "RelativeCreated": "relativeCreated",
        "Thread":          "thread",
        "ThreadName":      "threadName",
        "Process":         "process",
        "Message":         "message"
    }"""

    try:
        config: Dict = LoadConfig.load_correct_config_dict()
    except Exception as e:
        raise HanaInjectorError(
            "Please, check the error and define the env variable HANA_INJECTOR_CONFIG_FILE_PATH."
        ) from e

    @classmethod
    def _get_logger(cls, name):
        """
        Get the logger
        """

        if cls.loggers.get(name):
            return cls.loggers.get(name)
        else:
            try:
                log_mode: str = cls.config["hana_injector"]["log_mode"]
            except Exception as e:
                raise HanaInjectorError(
                    "Please, check the error and define the error log_mode parameter inside the config file."
                ) from e

            logger = logging.getLogger(name)
            logger.setLevel(CustomLogger._get_log_level_parameter(log_mode))
            logger.propagate = False

            handler = logging.StreamHandler()
            formatter = JsonFormatter(cls.log_format)
            handler.setFormatter(formatter)

            logger.addHandler(handler)
            cls.loggers[name] = logger

            return logger

    @classmethod
    def write_to_console(cls, status, message):
        """
        Log message to log file
        """

        if cls.config is None:
            raise HanaInjectorError(
                "Can't parse the config yaml. Please, define a valid config yaml"
            ) from Exception

        try:
            if cls.config["hana_injector"]["log_mode"] != "debug":
                if status == "error" or status == "warning":
                    CustomLogger._get_correct_status(
                        CustomLogger._get_logger("hana_injector"), status, message
                    )
            else:
                CustomLogger._get_correct_status(
                    CustomLogger._get_logger("hana_injector"), status, message
                )
        except (KeyError, ValueError):
            raise ValueError(
                "Value not available. Please, set the correct parameter: hana_injector.log_mode"
            )

    @staticmethod
    def _get_correct_status(logger, status, message):
        """
        Find correct status code
        """

        if status == "error":
            logger.error(message)
        elif status == "warning":
            logger.warning(message)
        elif status == "information":
            logger.info(message)
        else:
            logger.error("Error, by declaration the right logger status.")

    @staticmethod
    def _get_log_level_parameter(config_log_parameter: str):
        """
        log_level_parameter: object
        Get correct log level parameter
        """

        if config_log_parameter.lower() == "debug":
            log_level_parameter = logging.DEBUG
        elif config_log_parameter.lower() == "warning":
            log_level_parameter = logging.WARNING
        elif config_log_parameter.lower() == "information":
            log_level_parameter = logging.INFO
        elif config_log_parameter.lower() == "error":
            log_level_parameter = logging.ERROR
        else:
            log_level_parameter = logging.DEBUG

        return log_level_parameter
