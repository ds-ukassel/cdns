import requests
from requests import Session

from ranges.clickhouse_service import ClickhouseService


def fetch(url: str, session: Session | None = None) -> str:
    if session is None:
        response = requests.get(url)
    else:
        response = session.get(url)

    response.raise_for_status()
    return response.text

def get_networks(service: ClickhouseService, asn: int):
    query = "SELECT network FROM {{table}} WHERE asn={{asn:UInt32}}"
    return service.execute_query(query, parameters={"asn": asn})

def detect_range_type(range: str):
    if "." in range:
        return 4
    elif ":" in range:
        return 6
    else:
        raise ValueError("Unexpected network type")

