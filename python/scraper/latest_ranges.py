import json

from scraper.clickhouse_service import ClickhouseService
from scraper.config import CDN_DATABASE, CLICKHOUSE_CDN_DATABASE, CLICKHOUSE_CDN_TABLE


def main():
    with ClickhouseService(**CDN_DATABASE) as clickhouse:
        rows = clickhouse.execute_query(
            f"""
            SELECT
                cdn_name,
                groupArray(ip_range) AS ranges,
                max(timestamp) as timestamp
            FROM {CLICKHOUSE_CDN_DATABASE}.{CLICKHOUSE_CDN_TABLE}
            WHERE (cdn_name, timestamp) IN (
                SELECT cdn_name, max(timestamp)
                FROM {CLICKHOUSE_CDN_DATABASE}.{CLICKHOUSE_CDN_TABLE}
                GROUP BY cdn_name
            )
              AND source != 'ipinfo'
            GROUP BY cdn_name
            """
        ).result_rows

        print(json.dumps({
            row[0]: {
                "ranges": row[1],
                "timestamp": row[2].isoformat(),
            } for row in rows
        }))

if __name__ == "__main__":
    main()
