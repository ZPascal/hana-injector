import os
from typing import Dict
import yaml
from pathlib import Path


class LoadConfig:
    """The class includes all necessary methods to load the configuration from the config file"""

    @staticmethod
    def load_correct_config_dict() -> Dict:
        """The method includes a functionality to translate the configuration from a Yaml file and returns the configuration as a dictionary

        Raises:
            KeyError: Missed specifying a necessary configuration environment variable

        Returns:
            data (Dict): Returns the configuration as dictionary
        """

        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH") is None:
            raise KeyError(
                "Please, set the HANA_INJECTOR_CONFIG_FILE_PATH env variable."
            )

        path = Path(f"{os.environ.get('HANA_INJECTOR_CONFIG_FILE_PATH')}")
        with path.open("r", encoding="utf-8") as config_file:
            data: Dict = yaml.safe_load(config_file)

        return data
