import re
from typing import Iterable, Any

import clickhouse_connect
from clickhouse_connect.driver.query import QueryResult


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

    def execute_query(self, query: str, parameters: dict[str, Any] | None = None) -> QueryResult:
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", self.table):
            raise ValueError(f"Invalid table name: {self.table}")
        final_query = query.replace('{table}', self.table)
        return self.client.query(final_query, parameters=parameters)

    def insert_data(self, data, column_names: str | Iterable[str] = "*"):
        self.client.insert(self.table, data, column_names=column_names)

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
