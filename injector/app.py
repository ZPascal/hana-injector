import os

import prometheus_client
from broker_mqtt.mqtt import MQTT
from custom_logger.logger import CustomLogger, HanaInjectorError
from flask import Flask, Response, render_template
from flask.cli import FlaskGroup
from flask_bcrypt import Bcrypt
from flask_prometheus_metrics import register_metrics
from flask_wtf.csrf import CSRFProtect
from generator.generator import Generator
from load_config.config import LoadConfig
from waitress import serve
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

# Create a Bcrypt instance
bcrypt = Bcrypt(app)


def _init_application():
    """The method includes a functionality to initialize the application.

    Environment Variables:
        HANA_INJECTOR_CONFIG_FILE_PATH (str, required):
            Absolute or relative path to the YAML configuration file.
            Example: ``HANA_INJECTOR_CONFIG_FILE_PATH=config/config.yml``

        HANA_INJECTOR_GENERATOR_MODE (str, optional):
            Controls whether the code generator runs on startup.

            - **Not set** (default): The generator runs once and generates the
              converter, MQTT callback and SQL query code from the ``generator``
              section of the configuration file. Afterward the variable is
              internally set to ``"False"`` to prevent a second run within
              the same process.
            - **``"True"``**: The generator is explicitly enabled and executed.
            - **``"False"`` or any other value**: The generator is **skipped**.
              Use this when the generated source files (``converter/converter.py``,
              ``broker_mqtt/mqtt.py``, ``database_sql/sql.py``) already exist and
              shall not be overwritten, e.g. in production containers where the
              files were pre-generated during the image build.

            Example (skip generator)::

                export HANA_INJECTOR_GENERATOR_MODE="False"

    Raises:
        KeyError: Missed specifying a necessary configuration environment variable
        HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        ValueError: Missed specifying a necessary value

    Returns:
        None
    """

    if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH") is None:
        raise KeyError("Please, set the HANA_INJECTOR_CONFIG_FILE_PATH env variable.")

    try:
        config: dict = LoadConfig.load_correct_config_dict()
    except KeyError:
        raise KeyError("Please, check the error and define the env variable HANA_INJECTOR_CONFIG_FILE_PATH.")

    if (
        os.environ.get("HANA_INJECTOR_GENERATOR_MODE") is None
        or os.environ.get("HANA_INJECTOR_GENERATOR_MODE") == "True"
    ):
        try:
            Generator()
            os.environ["HANA_INJECTOR_GENERATOR_MODE"] = "False"
        except Exception as e:
            raise HanaInjectorError("An error has occurred. Please check the error log") from e

    try:
        app.config["SECRET_KEY"] = config["hana_injector"]["secret_key"]
    except Exception:
        raise ValueError("Value not available. Please, set the correct parameter: hana_injector.secret_key.")


@app.route("/health", methods=["GET"])
def _get_health_check():
    """The method includes a functionality to get the status of the health endpoint

    Returns:
        response (Response): Returns the positive status as HTTP response of the health endpoint
    """

    CustomLogger.write_to_console("information", "Health check, ok")
    return Response("Ok", status=200)


@app.route("/api/docs", methods=["GET"])
def _get_docs():
    """The method includes a functionality to get the documentation

    Returns:
        response (Response): Returns the documentation as HTTP response of the docs endpoint
    """

    return render_template("swaggerui.html")


def main(test: bool = False):
    """The method includes a functionality to start the application

    Returns:
        None
    """

    _init_application()

    manager = FlaskGroup(app)

    @manager.command
    def runserver():
        app.run()
        MQTT()

    register_metrics(app, app_version="0.0.1", app_config="production")
    dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": prometheus_client.make_wsgi_app()})

    config: dict = LoadConfig.load_correct_config_dict()

    if not test:
        serve(
            dispatcher,
            host=config["hana_injector"]["host"],
            port=config["hana_injector"]["port"],
            threads=config["hana_injector"]["threads"],
        )


# Create the server
if __name__ == "__main__":
    main()
