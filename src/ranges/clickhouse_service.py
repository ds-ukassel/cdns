import datetime
import re

import clickhouse_connect

from ranges.parser import IPResult

CLICKHOUSE_DATA_SCHEMA = """
    cdn_name String,
    timestamp DateTime64 DEFAULT now(),
    ip_range String,
    ip_version String
    """


class ClickhouseService:
    def __init__(self, host: str, port: int, user: str, password: str, database: str, table: str):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        self.table = table

        self.create_table(
            table=self.table,
            schema=CLICKHOUSE_DATA_SCHEMA,
        )

    def create_table(self, table: str, schema: str) -> None:
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
            raise ValueError(f"Invalid table name: {table}")
        schema = schema.strip()
        query = f"""
        CREATE OR REPLACE TABLE {table} (
            {schema}
        ) ENGINE = ReplacingMergeTree()
        ORDER BY (cdn_name, toYYYYMMDD(timestamp), ip_range)
        PARTITION BY toYYYYMM(timestamp)
        """
        self.client.command(query)

    def insert_data(self, timestamp: datetime.datetime, cdn: str, data: IPResult) -> None:
        ipv4_rows = [(cdn, timestamp, ip_range, "ipv4") for ip_range in data[0]]
        ipv6_rows = [(cdn, timestamp, ip_range, "ipv6") for ip_range in data[1]]
        self.client.insert(self.table, ipv4_rows + ipv6_rows)
