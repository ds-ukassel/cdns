import datetime
from pathlib import Path

from requests import Session

from common import config
from common.config import CDN_YAML
from common.logger import LOGGER
from common.utils import read_yaml
from ranges.clickhouse_service import ClickhouseService
from ranges.parser import PARSERS, Parser

from ranges.utils import get_networks, detect_range_type, insert_ranges


def main():
    LOGGER.info("Loading CDNs...")
    cdns = read_yaml(Path(CDN_YAML))
    LOGGER.info(f"Successfully loaded {len(cdns)} CDNs.")

    with (
        Session() as cdn_session,
        ClickhouseService(
            host=config.CLICKHOUSE_CDN_HOST,
            port=config.CLICKHOUSE_CDN_PORT,
            user=config.CLICKHOUSE_CDN_USER,
            password=config.CLICKHOUSE_CDN_PASSWORD,
            database=config.CLICKHOUSE_CDN_DATABASE,
            table=config.CLICKHOUSE_CDN_TABLE,
            secure=config.CLICKHOUSE_SECURE,
        ) as clickhouse_cdn, # cdn table
        ClickhouseService(
            host=config.CLICKHOUSE_IPINFO_HOST,
            port=config.CLICKHOUSE_IPINFO_PORT,
            user=config.CLICKHOUSE_IPINFO_USER,
            password=config.CLICKHOUSE_IPINFO_PASSWORD,
            database=config.CLICKHOUSE_IPINFO_DATABASE,
            table=config.CLICKHOUSE_IPINFO_TABLE,
            secure=config.CLICKHOUSE_SECURE
        ) as clickhouse_ipinfo
    ):
        for cdn in cdns:
            cdn_name = cdn.get('name')
            ranges = cdn.get("ranges", [])
            timestamp = datetime.datetime.now(datetime.timezone.utc)
            if not ranges:
                LOGGER.info(f"No ranges found for CDN '{cdn_name}'. Skipping...")
                continue
            for source in ranges:
                if "url" in source:
                    LOGGER.info(f"Processing URL source for CDN '{cdn_name}' (type: {source.get('range_type')})...")
                    parser: Parser = PARSERS.get(cdn.get("name"))
                    if not parser:
                        LOGGER.error(f"No parser found for CDN '{cdn_name}'. Skipping URL source...")
                        continue
                    try:
                        content = parser.fetch(source["url"], cdn_session)
                        ipv4_ranges, ipv6_ranges = parser.parse(content)
                        ipv4_rows = [(cdn_name, timestamp, ip_range, 4) for ip_range in ipv4_ranges]
                        ipv6_rows = [(cdn_name, timestamp, ip_range, 6) for ip_range in ipv6_ranges]
                        LOGGER.info(
                            f"Successfully parsed {len(ipv4_ranges)} IPv4 and {len(ipv6_ranges)} IPv6 ranges for CDN '{cdn_name}'.")
                        clickhouse_cdn.insert_data(ipv4_rows + ipv6_rows)
                        LOGGER.info(f"Successfully inserted ranges for CDN '{cdn_name}' into ClickHouse.")
                    except Exception:
                        LOGGER.exception(f"Error processing URL source for CDN '{cdn_name}'. Skipping...")
                elif "ranges" in source:
                    LOGGER.info(f"Processing static ranges for CDN '{cdn_name}'...")
                    ranges = source["ranges"]
                    range_type = source.get("range_type")

                    if range_type == "ipv4":
                        data = (cdn_name, timestamp, set(ranges), 4)
                        clickhouse_cdn.insert_data(data)
                        LOGGER.info(
                            f"Successfully inserted {len(ranges)} IPv4 ranges for CDN '{cdn_name}' into ClickHouse.")
                    elif range_type == "ipv6":
                        data = (cdn_name, timestamp, set(ranges), 6)
                        clickhouse_cdn.insert_data(data)
                        LOGGER.info(
                            f"Successfully inserted {len(ranges)} IPv6 ranges for CDN '{cdn_name}' into ClickHouse.")
                    else:
                        LOGGER.error(
                            f"Unknown range type '{range_type}' for CDN '{cdn_name}'. Skipping static ranges...")
                else:
                    LOGGER.error(f"No valid source found for CDN '{cdn_name}'. Skipping...")

            for asn in cdn.asns:
                LOGGER.info("Start fetching ranges from ipinfo ...")
                ip_ranges = get_networks(clickhouse_ipinfo, asn)
                for ip_range in ip_ranges:
                    try:
                        range_type = detect_range_type(ip_range)
                    except Exception:
                        LOGGER.exception(f"Error detecting network type for CDN '{cdn_name}' and ASN '{asn}'.")
                    data = (cdn_name, timestamp, range, range_type, "ipinfo") # TODO: adapt table format to source
                    clickhouse_cdn.insert_data(data)

        LOGGER.info("Done.")



if __name__ == "__main__":
    main()
