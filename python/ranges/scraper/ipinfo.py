import datetime
from typing import Any

from common.logger import LOGGER
from ranges.clickhouse_service import ClickhouseService
from ranges.utils import get_networks, detect_range_type


def get_ranges(clickhouse: ClickhouseService, timestamp: datetime.datetime, cdn: dict[str, Any]) -> list[tuple[str, datetime.datetime, str, int]]:
    cdn_name: str = cdn["name"]
    asns: list[int] = cdn.get("asns", [])
    if not asns:
        LOGGER.info(f"No asns found for CDN '{cdn_name}'. Skipping...")
        return []

    rows = []

    LOGGER.info("Start fetching ranges from IPInfo database...")

    for asn in cdn["asns"]:
        ip_ranges = get_networks(clickhouse, asn)
        for ip_range in ip_ranges:
            try:
                range_type = detect_range_type(ip_range)
            except Exception:
                LOGGER.exception(f"Error detecting network type for CDN '{cdn_name}' and ASN '{asn}'.")
                continue
            rows.append((cdn_name, timestamp, ip_range, range_type, "ipinfo"))

    LOGGER.info(f"Fetched {len(rows)} ranges for {len(cdn["asns"])} ASNs.")

    return rows
