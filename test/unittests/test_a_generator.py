import os
from unittest import TestCase
from unittest.mock import patch, mock_open, DEFAULT, Mock
from custom_logger.logger import HanaInjectorError
from load_config.config import LoadConfig


class GeneratorCase(TestCase):
    def setUp(self) -> None:
        from generator.generator import Generator
        Generator._generator_list = LoadConfig.load_correct_config_dict()["generator"]
        self.generator = Generator()

    def test_a_generate_mqtt_code_successful(self):
        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            f_1 = open(f"{os.getcwd()}/test/unittests/files/broker_mqtt/mqtt.py")
            f_2 = open(f"{os.getcwd()}/injector/broker_mqtt/mqtt.py")
        else:
            f_1 = open("files/broker_mqtt/mqtt.py")
            f_2 = open("../../injector/broker_mqtt/mqtt.py")

        self.assertListEqual(
            list(f_1.read()),
            list(f_2.read()),
        )
        f_1.close()
        f_2.close()

    def test_b_generate_converter_code_successful(self):
        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            f_1 = open(f"{os.getcwd()}/test/unittests/files/converter/converter.py")
            f_2 = open(f"{os.getcwd()}/injector/converter/converter.py")
        else:
            f_1 = open("files/converter/converter.py")
            f_2 = open("../../injector/converter/converter.py")

        self.assertListEqual(
            list(f_1.read()),
            list(f_2.read()),
        )
        f_1.close()
        f_2.close()

    def test_c_generate_sql_code_successful(self):
        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            f_1 = open(f"{os.getcwd()}/test/unittests/files/database_sql/sql.py")
            f_2 = open(f"{os.getcwd()}/injector/database_sql/sql.py")
        else:
            f_1 = open("files/database_sql/sql.py")
            f_2 = open("../../injector/database_sql/sql.py")

        self.assertListEqual(
            list(f_1.read()),
            list(f_2.read()),
        )
        f_1.close()
        f_2.close()

    @patch("generator.generator.Generator._generator_list")
    def test_d_generate_converter_no_generator_list(self, generator_list_mock):
        generator_list_mock.return_value = list()
        with self.assertRaises(HanaInjectorError):
            from generator.generator import Generator

            Generator()

    @patch("generator.generator.Generator._env.get_template")
    def test_e_generate_mqtt_code_no_template(self, template_mock):
        template_mock.side_effect = Exception
        with self.assertRaises(HanaInjectorError):
            from generator.generator import Generator

            Generator()

    @patch("jinja2.Template.render")
    def test_f_generate_mqtt_code_template_render_error(self, template_render_mock):
        template_render_mock.side_effect = ValueError
        with self.assertRaises(HanaInjectorError):
            from generator.generator import Generator

            Generator()

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_g_generate_mqtt_code_file_open_error(self, open_mock):
        open_mock.side_effect = Exception
        with self.assertRaises(HanaInjectorError):
            from generator.generator import Generator

            Generator()

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_h_reset_converter_code_no_template_file(self, open_mock):
        open_mock.side_effect = [DEFAULT, FileNotFoundError]
        with self.assertRaises(HanaInjectorError) as raises:
            from generator.generator import Generator

            Generator()
        self.assertEqual(
            str(raises.exception),
            str("File not found. Please, check the error"),
        )

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_i_reset_converter_code_no_file(self, open_mock):
        open_mock.side_effect = [DEFAULT, DEFAULT, FileNotFoundError]
        with self.assertRaises(HanaInjectorError) as raises:
            from generator.generator import Generator

            Generator()
        self.assertEqual(
            str(raises.exception),
            str("File not found. Please, check the error"),
        )

    @patch("generator.generator.Generator._env.get_template")
    def test_j_generate_converter_code_no_template(self, template_mock):
        template_mock.side_effect = Exception
        with self.assertRaises(HanaInjectorError):
            self.generator._generate_converter_code()

    @patch("jinja2.Template.render")
    def test_k_generate_converter_code_render_error(self, template_render_mock):
        template_render_mock.side_effect = ValueError
        with self.assertRaises(HanaInjectorError):
            self.generator._generate_converter_code()

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_l_generate_converter_code_file_error(self, open_mock):
        open_mock.side_effect = Exception
        with self.assertRaises(HanaInjectorError):
            self.generator._generate_converter_code()

    def test_get_mqtt_payload_values_empty_list(self):
        with self.assertRaises(HanaInjectorError):
            self.generator._get_mqtt_payload_values("test", list(), 1)

    @patch("subprocess.run")
    def test_format_converter_code_subprocess_error(self, subprocess_run_mock):
        mock: Mock = Mock()
        mock.returncode = 1
        subprocess_run_mock.return_value = mock

        with self.assertRaises(HanaInjectorError):
            self.generator._format_converter_code()

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_reset_sql_code_template_file_error(self, open_mock):
        open_mock.side_effect = FileNotFoundError
        with self.assertRaises(HanaInjectorError):
            self.generator._reset_sql_code()

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_reset_sql_code_file_error(self, open_mock):
        open_mock.side_effect = [DEFAULT, FileNotFoundError]
        with self.assertRaises(HanaInjectorError):
            self.generator._reset_sql_code()

    def test_write_sql_code_to_file_file_error(self):
        with self.assertRaises(HanaInjectorError):
            self.generator._write_sql_code_to_file("", "", "")

    @patch("generator.generator.Generator._write_sql_code_to_file")
    def test_create_sql_code_file_write_to_sql_file_error(
        self, write_sql_code_to_file_mock
    ):
        write_sql_code_to_file_mock.side_effect = Exception

        with self.assertRaises(HanaInjectorError):
            self.generator._Generator__create_sql_sep_code(
                ["sep:ListDict(Name, Amount)|OrderID, OrderDate"], 0
            )

    @patch("generator.generator.Generator._write_sql_code_to_file")
    def test_create_sql_base_code_file_write_to_sql_file_error(
        self, write_sql_code_to_file_mock
    ):
        write_sql_code_to_file_mock.side_effect = Exception

        with self.assertRaises(HanaInjectorError):
            self.generator._Generator__create_sql_base_code(
                ["str"], 0
            )

    def test_extract_mqtt_payload_values_no_supported_types_error(self):
        with self.assertRaises(HanaInjectorError):
            self.generator._Generator__extract_mqtt_payload_values(
                "test", [{"test": "sep:List(Name, Amount)|OrderID, OrderDate"}], 1
            )

    def test_extract_mqtt_payload_values_sep_mode(self):
        self.assertIsNotNone(self.generator._Generator__extract_mqtt_payload_values(
            "test", [{"test": "sep:ListDict(Name, Amount)|OrderID, OrderDate"}], 1
        ))

    def test_extract_sep_methods_sep_error(self):
        with self.assertRaises(HanaInjectorError):
            self.generator._Generator__extract_sep_methods(
                [{"test": "sep:List(Name, Amount)|OrderID, OrderDate"}],
                1,
                "test",
                1,
                "test",
            )
