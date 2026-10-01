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
