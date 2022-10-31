"""
Created on 18.02.2021

@author: Pascal Zimmermann
"""

import datetime

from custom_logger.custom_logger import HanaInjectorError
from database_sql.sql import SQL
from typing import Dict, List


# ===============================================================================
# Converter class to transform MQTT input to a SAP Hana database
# ===============================================================================
class Converter:
    _sql = SQL()

    # ==================================================================================================================
    # Method: service1 to transform data from mqtt to a hana database
    # ==================================================================================================================
    @staticmethod
    def service1(mosq, obj, msg):
        try:
            payload = eval(str(msg.payload.decode("utf-8")))

            orderid: str = payload["OrderID"]
            orderdate: datetime = datetime.datetime.strptime(
                payload["OrderDate"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            color: List = payload["Color"]
            color2: List = payload["Color2"]
            customername: str = payload["CustomerName"]

            SQL.service1_1(orderid, orderdate, color, color2, customername)

            for i in range(0, len(color)):
                attributes = eval(str(color[i]))
                SQL.service1_sep1(
                    orderid, orderdate, attributes["Name"], attributes["Amount"]
                )
            for i in range(0, len(color2)):
                attributes = eval(str(color2[i]))
                SQL.service1_sep2(
                    orderid, orderdate, attributes["Name"], attributes["Amount"]
                )
        except Exception as e:
            raise HanaInjectorError(
                f"Maybe the values are not correct. Please check the error message"
            ) from e

    # ==================================================================================================================
    # Method: service2 to transform data from mqtt to a hana database
    # ==================================================================================================================
    @staticmethod
    def service2(mosq, obj, msg):
        try:
            payload = eval(str(msg.payload.decode("utf-8")))

            orderid: str = payload["OrderID"]
            orderdate: datetime = datetime.datetime.strptime(
                payload["OrderDate"], "%Y-%m-%d"
            ).date()
            customername: str = payload["CustomerName"]
            color: List = payload["Color"]

            SQL.service2_1(orderid, orderdate, customername, color)
            SQL.service2_2(orderid, orderdate, customername, color)

        except Exception as e:
            raise HanaInjectorError(
                f"Maybe the values are not correct. Please check the error message"
            ) from e

    # ==================================================================================================================
    # Method: service3 to transform data from mqtt to a hana database
    # ==================================================================================================================
    @staticmethod
    def service3(mosq, obj, msg):
        try:
            payload = eval(str(msg.payload.decode("utf-8")))

            orderid: str = payload["OrderID"]
            deviceid: str = payload["DeviceID"]
            orderdate: str = payload["OrderDate"]
            statuscode: str = payload["StatusCode"]

            SQL.service3_1(orderid, deviceid, orderdate, statuscode)

        except Exception as e:
            raise HanaInjectorError(
                f"Maybe the values are not correct. Please check the error message"
            ) from e
