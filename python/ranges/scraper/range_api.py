import datetime
from typing import Any

from requests import Session

from common.logger import LOGGER
from ranges.parser import PARSERS, Parser

RANGE_SOURCE_API = "api"
RANGE_SOURCE_STATIC = "static"


def get_ranges(session: Session, timestamp: datetime.datetime, cdn: dict[str, Any]) -> list[tuple[str, datetime.datetime, str, int, str]]:
    cdn_name: str = cdn["name"]
    sources: list[dict[str, Any]] = cdn.get("ranges", [])
    if not sources:
        LOGGER.info(f"No ranges found for CDN '{cdn_name}'. Skipping...")
        return []

    rows = []

    for source in sources:
        if "url" in source:
            LOGGER.info(f"Processing URL source for CDN '{cdn_name}' (type: {source.get('range_type')})...")
            parser: Parser = PARSERS.get(cdn.get("name"))
            if not parser:
                LOGGER.error(f"No parser found for CDN '{cdn_name}'. Skipping URL source...")
                continue
            try:
                content = parser.fetch(source["url"], session)
                ipv4_ranges, ipv6_ranges = parser.parse(content)
                ipv4_rows = [(cdn_name, timestamp, ip_range, 4, RANGE_SOURCE_API) for ip_range in ipv4_ranges]
                ipv6_rows = [(cdn_name, timestamp, ip_range, 6, RANGE_SOURCE_API) for ip_range in ipv6_ranges]
                LOGGER.info(f"Successfully parsed {len(ipv4_ranges)} IPv4 and {len(ipv6_ranges)} IPv6 ranges for CDN '{cdn_name}'.")
                rows += (ipv4_rows + ipv6_rows)
                LOGGER.info(f"Successfully added ranges for CDN '{cdn_name}' into ClickHouse.")
            except Exception:
                LOGGER.exception(f"Error processing URL source for CDN '{cdn_name}'. Skipping...")
        elif "ranges" in source:
            LOGGER.info(f"Processing static ranges for CDN '{cdn_name}'...")
            static_ranges = source["ranges"]
            range_type = source.get("range_type")

            if range_type == "ipv4":
                rows += [(cdn_name, timestamp, ip_range, 4, RANGE_SOURCE_STATIC) for ip_range in static_ranges]
                LOGGER.info(f"Successfully added {len(static_ranges)} IPv4 ranges for CDN '{cdn_name}' into ClickHouse.")
            elif range_type == "ipv6":
                rows += [(cdn_name, timestamp, ip_range, 6, RANGE_SOURCE_STATIC) for ip_range in static_ranges]
                LOGGER.info(f"Successfully added {len(static_ranges)} IPv6 ranges for CDN '{cdn_name}' into ClickHouse.")
            else:
                LOGGER.error(f"Invalid range type '{range_type}' for static ranges of CDN '{cdn_name}'. Skipping static ranges...")
        else:
            LOGGER.error(f"No valid source found for CDN '{cdn_name}'. Skipping...")

    return rows
