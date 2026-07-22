import datetime
import re

import clickhouse_connect

from ranges.parser import IPResult


class ClickhouseService:
    def __init__(self, host: str, port: int, user: str, password: str, database: str, table: str, secure: bool = False):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            secure=secure,
        )

        self.table = table
        self.create_table()

    def create_table(self) -> None:
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", self.table):
            raise ValueError(f"Invalid table name: {self.table}")

        query = f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                cdn_name String,
                timestamp DateTime64 DEFAULT now(),
                ip_range String,
                ip_version UInt8
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (cdn_name, toYYYYMMDD(timestamp), ip_range)
            PARTITION BY toYYYYMM(timestamp)
            """
        self.client.command(query)

    def insert_data(self, timestamp: datetime.datetime, cdn: str, data: IPResult) -> None:
        ipv4_rows = [(cdn, timestamp, ip_range, 4) for ip_range in data[0]]
        ipv6_rows = [(cdn, timestamp, ip_range, 6) for ip_range in data[1]]
        self.client.insert(self.table, ipv4_rows + ipv6_rows)

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
