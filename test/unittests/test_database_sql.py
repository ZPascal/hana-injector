import os
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock


class SQLTestCase(TestCase):
    @patch("pyhdb.connect")
    def setUp(self, pyhdb_connect_mock) -> None:
        mock_cursor = Mock()
        mock_cursor.execute = MagicMock()

        mock = Mock()
        mock.cursor = mock_cursor
        mock.commit = MagicMock()
        mock.close = MagicMock()

        pyhdb_connect_mock.return_value = mock

        from database_sql.sql import SQL
        self.sql = SQL()

    @patch.dict(os.environ, {"HANA_INJECTOR_GENERATOR_MODE": "False"})
    def test_create_database_connection_successful(self):
        self.assertIn("database_sql.sql.SQL", str(self.sql))
