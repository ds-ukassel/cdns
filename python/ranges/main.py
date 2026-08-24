import datetime
from pathlib import Path

from requests import Session

from common import config
from common.config import CDN_YAML
from common.logger import LOGGER
from common.utils import read_yaml
from ranges.clickhouse_service import ClickhouseService
from ranges.parser import PARSERS, Parser


def main():
    LOGGER.info("Loading CDNs...")
    cdns = read_yaml(Path(CDN_YAML))
    LOGGER.info(f"Successfully loaded {len(cdns)} CDNs.")

    with (
        Session() as session,
        ClickhouseService(
            host=config.CLICKHOUSE_HOST,
            port=config.CLICKHOUSE_PORT,
            user=config.CLICKHOUSE_USER,
            password=config.CLICKHOUSE_PASSWORD,
            database=config.CLICKHOUSE_DATABASE,
            table=config.CLICKHOUSE_TABLE,
            secure=config.CLICKHOUSE_SECURE,
        ) as clickhouse
    ):
        for cdn in cdns:
            ranges = cdn.get("ranges", [])
            if not ranges:
                LOGGER.info(f"No ranges found for CDN '{cdn.get('name')}'. Skipping...")
                continue
            for source in ranges:
                timestamp = datetime.datetime.now(datetime.timezone.utc)
                if "url" in source:
                    LOGGER.info(f"Processing URL source for CDN '{cdn.get('name')}' (type: {source.get('range_type')})...")
                    parser: Parser = PARSERS.get(cdn.get("name"))
                    if not parser:
                        LOGGER.error(f"No parser found for CDN '{cdn.get('name')}'. Skipping URL source...")
                        continue
                    try:
                        content = parser.fetch(source["url"], session)
                        ipv4_ranges, ipv6_ranges = parser.parse(content)
                        LOGGER.info(
                            f"Successfully parsed {len(ipv4_ranges)} IPv4 and {len(ipv6_ranges)} IPv6 ranges for CDN '{cdn.get('name')}'.")
                        clickhouse.insert_data(timestamp, cdn.get("name"), (ipv4_ranges, ipv6_ranges))
                        LOGGER.info(f"Successfully inserted ranges for CDN '{cdn.get('name')}' into ClickHouse.")
                    except Exception:
                        LOGGER.exception(f"Error processing URL source for CDN '{cdn.get('name')}'. Skipping...")
                elif "ranges" in source:
                    LOGGER.info(f"Processing static ranges for CDN '{cdn.get('name')}'...")
                    ranges = source["ranges"]
                    range_type = source.get("range_type")

                    if range_type == "ipv4":
                        clickhouse.insert_data(timestamp, cdn.get("name"), (set(ranges), set()))
                        LOGGER.info(
                            f"Successfully inserted {len(ranges)} IPv4 ranges for CDN '{cdn.get('name')}' into ClickHouse.")
                    elif range_type == "ipv6":
                        clickhouse.insert_data(timestamp, cdn.get("name"), (set(), set(ranges)))
                        LOGGER.info(
                            f"Successfully inserted {len(ranges)} IPv6 ranges for CDN '{cdn.get('name')}' into ClickHouse.")
                    else:
                        LOGGER.error(
                            f"Unknown range type '{range_type}' for CDN '{cdn.get('name')}'. Skipping static ranges...")
                else:
                    LOGGER.error(f"No valid source found for CDN '{cdn.get('name')}'. Skipping...")


if __name__ == "__main__":
    main()
