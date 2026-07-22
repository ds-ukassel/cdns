import os

CDN_YAML: str = os.getenv("CDN_YAML", "cdns.yaml")

CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT: int = int(os.getenv("CLICKHOUSE_PORT", 8123))
CLICKHOUSE_USER: str = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "default")
CLICKHOUSE_DATABASE: str = os.getenv("CLICKHOUSE_DATABASE", "default")
CLICKHOUSE_TABLE: str = os.getenv("CLICKHOUSE_TABLE", "cdn_ip_ranges")
CLICKHOUSE_SECURE: bool = os.getenv("CLICKHOUSE_SECURE", "false").lower() == "true"
