"""
Created on 18.02.2021

@author: Pascal Zimmermann
"""

import os
from typing import Dict
from ruamel.yaml import YAML
from pathlib import Path


class LoadConfig:
    """
    Config loader class
    """

    @staticmethod
    def load_correct_config_dict() -> Dict:
        """
        Get a variable or message back and load the config environment
        """

        if os.environ.get("HANA_INJECTOR_CONFIG_FILE_PATH") is None:
            raise KeyError(
                "Please, set the HANA_INJECTOR_CONFIG_FILE_PATH env variable."
            )

        path = Path(f"{os.environ.get('HANA_INJECTOR_CONFIG_FILE_PATH')}")
        yaml = YAML(typ="safe")
        data: Dict = yaml.load(path)

        return data
