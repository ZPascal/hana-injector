import os
from unittest import TestCase
from unittest.mock import patch, Mock


class AppCase(TestCase):
    @patch.dict(os.environ, {"HANA_INJECTOR_GENERATOR_MODE": "False"})
    def test_get_health_check_successful(self):
        from app import _get_health_check

        self.assertEqual(str(_get_health_check()), str("<Response 2 bytes [200 OK]>"))

    @patch.dict(os.environ, {"HANA_INJECTOR_GENERATOR_MODE": "False"})
    def test_get_docs_check(self):
        from app import _get_docs

        with self.assertRaises(RuntimeError):
            _get_docs()

    @patch.dict(os.environ, {"HANA_INJECTOR_GENERATOR_MODE": "False"})
    def test_a_init_application_no_generation(self):
        from app import _init_application

        self.assertIsNone(_init_application())

    @patch("load_config.config.LoadConfig.load_correct_config_dict")
    def test_b_init_application_no_correct_config_available(
        self, load_correct_config_dict_mock
    ):
        load_correct_config_dict_mock.side_effect = KeyError
        with self.assertRaises(KeyError) as raises:
            from app import _init_application

            _init_application()

        self.assertEqual(
            str(raises.exception),
            str(
                KeyError(
                    "Please, check the error and define the env variable HANA_INJECTOR_CONFIG_FILE_PATH."
                )
            ),
        )

    def test_c_init_application_no_config_file_error(self):
        del os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"]
        with self.assertRaises(KeyError) as raises:
            from app import _init_application

            _init_application()
        self.assertEqual(
            str(raises.exception),
            str(
                KeyError("Please, set the HANA_INJECTOR_CONFIG_FILE_PATH env variable.")
            ),
        )
        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = os.environ.get(
                "HANA_INJECTOR_CONFIG_FILE_PATH_2"
            )
        else:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = "config/config.yml"

    @patch("generator.generator.Generator", Mock(return_value=None))
    @patch.dict(os.environ, {"HANA_INJECTOR_GENERATOR_MODE": "True"})
    def test_d_init_application_generator(self):
        from app import _init_application

        _init_application()

        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = os.environ.get(
                "HANA_INJECTOR_CONFIG_FILE_PATH_2"
            )
        else:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = "config/config.yml"

    @patch("app.app")
    @patch.dict(os.environ, {"HANA_INJECTOR_GENERATOR_MODE": "False"})
    def test_e_init_application_no_app_config(self, app_config_mock):
        app_config_mock.config.return_value = None

        from app import _init_application

        _init_application()

        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = os.environ.get(
                "HANA_INJECTOR_CONFIG_FILE_PATH_2"
            )
        else:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = "config/config.yml"

    @patch.dict(os.environ, {"HANA_INJECTOR_GENERATOR_MODE": "False"})
    @patch.dict(
        os.environ,
        {
            "HANA_INJECTOR_CONFIG_FILE_PATH": f"{os.getcwd()}/config/config_no_secret_key.yml"
        },
    )
    def test_f_init_application_no_app_config_error(self):
        with self.assertRaises(ValueError):
            from app import _init_application

            _init_application()

        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH_2") is not None:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = os.environ.get(
                "HANA_INJECTOR_CONFIG_FILE_PATH_2"
            )
        else:
            os.environ["HANA_INJECTOR_CONFIG_FILE_PATH"] = "config/config.yml"
