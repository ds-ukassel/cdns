from pathlib import Path
from typing import Any

import requests
import yaml
from requests import Session

from scraper.clickhouse_service import ClickhouseService

from scraper.logger import LOGGER


def fetch(url: str, session: Session | None = None) -> str:
    if session is None:
        response = requests.get(url)
    else:
        response = session.get(url)

    response.raise_for_status()
    return response.text


def get_networks(service: ClickhouseService, asn: int) -> list[str]:
    result = service.execute_query("SELECT network FROM {table} WHERE asn={asn:UInt32}", parameters={"asn": asn})
    return [row[0] for row in result.result_rows]


def detect_range_type(ip_range: str):
    if "." in ip_range:
        return 4
    elif ":" in ip_range:
        return 6
    else:
        raise ValueError("Unexpected network type")

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
