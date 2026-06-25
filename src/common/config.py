import os

CDN_YAML: str = os.getenv("CDN_YAML", "cdns.yaml")

CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT: int = int(os.getenv("CLICKHOUSE_PORT", 8123))
CLICKHOUSE_USER: str = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "default")
CLICKHOUSE_DATABASE: str = os.getenv("CLICKHOUSE_DATABASE", "default")
CLICKHOUSE_TABLE: str = os.getenv("CLICKHOUSE_TABLE", "cdn_ip_ranges")

MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "ip-ranges")
MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() in ("true", "1", "yes")
