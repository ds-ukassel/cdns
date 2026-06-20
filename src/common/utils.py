from pathlib import Path
from typing import Any

import yaml

from common.logger import LOGGER


def read_yaml(file_path: Path, default_value: Any = None) -> Any:
    """
    Reads a YAML file and returns its content.
    :param file_path: Path to the YAML file.
    :param default_value: Default value to return if an error occurs while reading the file.
    :return: Content of the YAML file or default value (None by default) if an error occurs.
    """
    with open(file_path) as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError:
            LOGGER.error(f"Error reading YAML file '{file_path}'. Returning default...")
            return default_value
