import datetime
from pathlib import Path

from requests import Session

from scraper.config import *
from scraper.logger import LOGGER
from scraper.utils import read_yaml
from scraper.clickhouse_service import ClickhouseService
from scraper.scraper import range_api, ipinfo

CDN_DATABASE = {
    "host": CLICKHOUSE_CDN_HOST,
    "port": CLICKHOUSE_CDN_PORT,
    "user": CLICKHOUSE_CDN_USER,
    "password": CLICKHOUSE_CDN_PASSWORD,
    "database": CLICKHOUSE_CDN_DATABASE,
    "table": CLICKHOUSE_CDN_TABLE,
    "secure": CLICKHOUSE_SECURE
}

IPINFO_DATABASE = {
    "host": CLICKHOUSE_IPINFO_HOST,
    "port": CLICKHOUSE_IPINFO_PORT,
    "user": CLICKHOUSE_IPINFO_USER,
    "password": CLICKHOUSE_IPINFO_PASSWORD,
    "database": CLICKHOUSE_IPINFO_DATABASE,
    "table": CLICKHOUSE_IPINFO_TABLE,
    "secure": CLICKHOUSE_SECURE
}


def main():
    LOGGER.info("Loading CDNs...")
    cdns = read_yaml(Path(CDN_YAML))
    LOGGER.info(f"Successfully loaded {len(cdns)} CDNs.")

    timestamp = datetime.datetime.now(datetime.timezone.utc)

    with (
        Session() as cdn_session,
        ClickhouseService(**CDN_DATABASE) as clickhouse_cdn,
        ClickhouseService(**IPINFO_DATABASE) as clickhouse_ipinfo
    ):
        LOGGER.info("Scraping ranges...")
        for cdn in cdns:
            LOGGER.info(f"Scraping ranges for {cdn["name"]}...")
            api_ranges = range_api.get_ranges(cdn_session, timestamp, cdn)
            ipinfo_ranges = ipinfo.get_ranges(clickhouse_ipinfo, timestamp, cdn)
            clickhouse_cdn.insert_data(api_ranges + ipinfo_ranges)
        LOGGER.info("Done.")


if __name__ == "__main__":
    main()
