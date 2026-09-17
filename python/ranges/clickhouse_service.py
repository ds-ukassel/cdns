import clickhouse_connect

from ranges.parser import IPResult


class ClickhouseService:
    def __init__(self, host: str, port: int, user: str, password: str, database: str, secure: bool = False):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            secure=secure,
        )

    def execute_query(self, query: str, parameters: str) -> None:
        self.client.command(query, parameters=parameters)

    def insert_data(self, table: str, data, column_names=None):
        self.client.insert(table, data, column_names=column_names)

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
