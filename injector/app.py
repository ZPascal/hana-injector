import os
from typing import Dict

from flask import Flask, Response, render_template
from flask.cli import FlaskGroup
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from waitress import serve
import prometheus_client
from flask_prometheus_metrics import register_metrics
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from generator.generator import Generator
from broker_mqtt.mqtt import MQTT
from load_config.config import LoadConfig
from custom_logger.logger import CustomLogger, HanaInjectorError

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

# Create a Bcrypt instance
bcrypt = Bcrypt(app)


def _init_application():
    """The method includes a functionality to initialize the application

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
        config: Dict = LoadConfig.load_correct_config_dict()
    except KeyError:
        raise KeyError(
            "Please, check the error and define the env variable HANA_INJECTOR_CONFIG_FILE_PATH."
        )

    if (
        os.environ.get("HANA_INJECTOR_GENERATOR_MODE") is None
        or bool(os.environ.get("HANA_INJECTOR_GENERATOR_MODE")) is True
    ):
        try:
            Generator()
            os.environ["HANA_INJECTOR_GENERATOR_MODE"] = "False"
        except Exception as e:
            raise HanaInjectorError(
                "An error has occurred. Please check the error log"
            ) from e

    try:
        app.config["SECRET_KEY"] = config["hana_injector"]["secret_key"]
    except Exception:
        raise ValueError(
            "Value not available. Please, set the correct parameter: hana_injector.secret_key."
        )


@app.route("/health", methods=['GET'])
def _get_health_check():
    """The method includes a functionality to get the status of the health endpoint

    Returns:
        response (Response): Returns the positive status as HTTP response of the health endpoint
    """

    CustomLogger.write_to_console("information", "Health check, ok")
    return Response("Ok", status=200)


@app.route("/api/docs", methods=['GET'])
def _get_docs():
    """The method includes a functionality to get the documentation

    Returns:
        response (Response): Returns the documentation as HTTP response of the docs endpoint
    """

    return render_template("swaggerui.html")


# Create the server
if __name__ == "__main__":
    _init_application()

    manager = FlaskGroup(app)

    @manager.command
    def runserver():
        app.run()
        MQTT()

    register_metrics(app, app_version="0.0.1", app_config="production")
    dispatcher = DispatcherMiddleware(
        app.wsgi_app, {"/metrics": prometheus_client.make_wsgi_app()}
    )

    config: Dict = LoadConfig.load_correct_config_dict()
    serve(dispatcher, host=config["hana_injector"]["host"], port=config["hana_injector"]["8080"],
          threads=config["hana_injector"]["threads"])
