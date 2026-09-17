import os

CDN_YAML: str = os.getenv("CDN_YAML", "cdns.yaml")

CLICKHOUSE_CDN_HOST: str = os.getenv("CLICKHOUSE_CDN_HOST", "localhost")
CLICKHOUSE_CDN_PORT: int = int(os.getenv("CLICKHOUSE_CDN_PORT", 8123))
CLICKHOUSE_CDN_USER: str = os.getenv("CLICKHOUSE_CDN_USER", "default")
CLICKHOUSE_CDN_PASSWORD: str = os.getenv("CLICKHOUSE_CDN_PASSWORD", "default")
CLICKHOUSE_CDN_DATABASE: str = os.getenv("CLICKHOUSE_CDN_DATABASE", "default")
CLICKHOUSE_CDN_TABLE: str = os.getenv("CLICKHOUSE_CDN_TABLE", "cdn_ip_ranges")
CLICKHOUSE_SECURE: bool = os.getenv("CLICKHOUSE_SECURE", "false").lower() == "true"

CLICKHOUSE_IPINFO_HOST: str = os.getenv("CLICKHOUSE_IPINFO_HOST", "localhost")
CLICKHOUSE_IPINFO_PORT: int = int(os.getenv("CLICKHOUSE_IPINFO_PORT", 8123))
CLICKHOUSE_IPINFO_USER: str = os.getenv("CLICKHOUSE_IPINFO_USER", "default")
CLICKHOUSE_IPINFO_PASSWORD: str = os.getenv("CLICKHOUSE_IPINFO_PASSWORD", "default")
CLICKHOUSE_IPINFO_DATABASE: str = os.getenv("CLICKHOUSE_IPINFO_DATABASE", "default")
CLICKHOUSE_IPINFO_TABLE: str = os.getenv("CLICKHOUSE_IPINFO_TABLE", "cdn_ip_ranges")
