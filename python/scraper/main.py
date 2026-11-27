import datetime
from pathlib import Path

from requests import Session

from scraper.config import CDN_YAML, CDN_DATABASE, IPINFO_DATABASE
from scraper.logger import LOGGER
from scraper.utils import read_yaml
from scraper.clickhouse_service import ClickhouseService
from scraper.scraper import range_api, ipinfo


def main():
    cdns = read_yaml(Path(CDN_YAML))

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
