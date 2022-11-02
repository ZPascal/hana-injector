import os
import pyhdb
import socket

from load_config.config import LoadConfig
from custom_logger.logger import HanaInjectorError, CustomLogger


class SQL:
    """The class includes all necessary methods to convert and transform MQTT input streams to an SAP Hana database"""

    _config = LoadConfig.load_correct_config_dict()

    # Connection to the Database
    if (
        _config["hana_database"]["username"] == ""
        or _config["hana_database"]["username"] is None
        and _config["hana_database"]["password"] == ""
        or _config["hana_database"]["password"] is None
    ):
        raise HanaInjectorError(
            "Value not available. Please, set the correct "
            "parameter: hana_database.username or hana_database.password",
        ) from ValueError

    if (
        _config["hana_database"]["hostname"] == ""
        or _config["hana_database"]["hostname"] is None
        and _config["hana_database"]["port"] == 0
        or _config["hana_database"]["port"] is None
    ):
        raise HanaInjectorError(
            "Value not available. Please, set the correct "
            "parameter: hana_database.hostname or hana_database.port",
        ) from ValueError

    try:
        # Create the connection to the Database

        if bool(os.environ.get("HANA_INJECTOR_GENERATOR_MODE")) is False:
            _conn = pyhdb.connect(
                host=_config["hana_database"]["hostname"],
                port=_config["hana_database"]["port"],
                user=_config["hana_database"]["username"],
                password=_config["hana_database"]["password"],
            )

            CustomLogger.write_to_console(
                "information",
                "Connected with the Hana DB",
            )
    except (pyhdb.Error, socket.gaierror) as e:
        raise HanaInjectorError(
            "Error at the database connection, please repeat it.",
        ) from e

    @classmethod
    def service1_sep1(cls, orderid, orderdate, name, amount):
        """The service1_sep1 method includes a functionality to insert data into a hana database

        Args:
            args (any): Specify the dynamically generated forwarded values as dummy value

        Returns:
            None
        """

        # Connection to the Database
        cursor = cls._conn.cursor()

        sql = "Test1_sep"
        cursor.execute(sql, (orderid, orderdate, name, amount))

        # Finish the connection to the database
        cls._conn.commit()

        CustomLogger.write_to_console("information", "Execute method service1_sep1")
        cls._conn.close()

    @classmethod
    def service1_sep2(cls, orderid, orderdate, name, amount):
        """The service1_sep2 method includes a functionality to insert data into a hana database

        Args:
            args (any): Specify the dynamically generated forwarded values as dummy value

        Returns:
            None
        """

        # Connection to the Database
        cursor = cls._conn.cursor()

        sql = "Test2_sep"
        cursor.execute(sql, (orderid, orderdate, name, amount))

        # Finish the connection to the database
        cls._conn.commit()

        CustomLogger.write_to_console("information", "Execute method service1_sep2")
        cls._conn.close()

    @classmethod
    def service1_1(cls, orderid, orderdate, customername):
        """The service1_1 method includes a functionality to insert data into a hana database

        Args:
            args (any): Specify the dynamically generated forwarded values as dummy value

        Returns:
            None
        """

        # Connection to the Database
        cursor = cls._conn.cursor()

        sql = "Test1"
        cursor.execute(sql, (orderid, orderdate, customername))

        # Finish the connection to the database
        cls._conn.commit()

        CustomLogger.write_to_console("information", "Execute method service1_1")
        cls._conn.close()

    @classmethod
    def service2_1(cls, orderid, orderdate, customername, color):
        """The service2_1 method includes a functionality to insert data into a hana database

        Args:
            args (any): Specify the dynamically generated forwarded values as dummy value

        Returns:
            None
        """

        # Connection to the Database
        cursor = cls._conn.cursor()

        sql = "Test2"
        cursor.execute(sql, (orderid, orderdate, customername, color))

        # Finish the connection to the database
        cls._conn.commit()

        CustomLogger.write_to_console("information", "Execute method service2_1")
        cls._conn.close()

    @classmethod
    def service2_2(cls, orderid, orderdate, customername, color):
        """The service2_2 method includes a functionality to insert data into a hana database

        Args:
            args (any): Specify the dynamically generated forwarded values as dummy value

        Returns:
            None
        """

        # Connection to the Database
        cursor = cls._conn.cursor()

        sql = "Test22"
        cursor.execute(sql, (orderid, orderdate, customername, color))

        # Finish the connection to the database
        cls._conn.commit()

        CustomLogger.write_to_console("information", "Execute method service2_2")
        cls._conn.close()

    @classmethod
    def service3_1(cls, orderid, deviceid, orderdate, statuscode):
        """The service3_1 method includes a functionality to insert data into a hana database

        Args:
            args (any): Specify the dynamically generated forwarded values as dummy value

        Returns:
            None
        """

        # Connection to the Database
        cursor = cls._conn.cursor()

        sql = "Test3"
        cursor.execute(sql, (orderid, deviceid, orderdate, statuscode))

        # Finish the connection to the database
        cls._conn.commit()

        CustomLogger.write_to_console("information", "Execute method service3_1")
        cls._conn.close()
