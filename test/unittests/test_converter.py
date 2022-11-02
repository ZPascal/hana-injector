import datetime

from unittest import TestCase
from unittest.mock import patch, Mock
from custom_logger.logger import HanaInjectorError


class ConverterTestCase(TestCase):

    def test_service1_error(self):
        with self.assertRaises(HanaInjectorError):
            from converter.converter import Converter
            Converter.service1("test", "test", "test")

    @patch("database_sql.sql.SQL.service1_sep2")
    @patch("database_sql.sql.SQL.service1_sep1")
    @patch("database_sql.sql.SQL.service1_1")
    def test_service1(self, service1_1_mock, service1_sep1_mock, service1_sep2_mock):
        msg_mock: Mock = Mock()
        msg_mock.payload.decode = Mock(
            return_value=str(
                dict(
                    {
                        "OrderID": "test",
                        "OrderDate": datetime.datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "CustomerName": "test",
                        "Color": [{"Name": "test", "Amount": "test"}],
                        "Color2": [{"Name": "test", "Amount": "test"}],
                    }
                )
            )
        )

        from converter.converter import Converter

        Converter.service1("test", "test", msg_mock)

        service1_1_mock.assert_called_once()
        service1_sep1_mock.assert_called_once()
        service1_sep2_mock.assert_called_once()

    def test_service2_error(self):
        with self.assertRaises(HanaInjectorError):
            from converter.converter import Converter
            Converter.service2("test", "test", "test")

    @patch("database_sql.sql.SQL.service2_2")
    @patch("database_sql.sql.SQL.service2_1")
    def test_service2(self, service2_1_mock, service2_2_mock):
        msg_mock: Mock = Mock()
        msg_mock.payload.decode = Mock(
            return_value=str(
                dict(
                    {
                        "OrderID": "test",
                        "OrderDate": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "CustomerName": "test",
                        "Color": ["test", "test"],
                    }
                )
            )
        )

        from converter.converter import Converter

        Converter.service2("test", "test", msg_mock)

        service2_1_mock.assert_called_once()
        service2_2_mock.assert_called_once()

    def test_service3_error(self):
        with self.assertRaises(HanaInjectorError):
            from converter.converter import Converter
            Converter.service3("test", "test", "test")

    @patch("database_sql.sql.SQL.service3_1")
    def test_service3(self, service3_1_mock):
        msg_mock: Mock = Mock()
        msg_mock.payload.decode = Mock(
            return_value=str(
                dict(
                    {
                        "OrderID": "test",
                        "DeviceID": "test",
                        "OrderDate": datetime.datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "StatusCode": "test",
                    }
                )
            )
        )

        from converter.converter import Converter

        Converter.service3("test", "test", msg_mock)

        service3_1_mock.assert_called_once()
