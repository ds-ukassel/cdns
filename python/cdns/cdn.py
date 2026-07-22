from dataclasses import dataclass
from typing import Literal


@dataclass
class CDN:
    name: str
    domains: list[str]
    headers: list[dict[str, str | None]]
    ranges: list[IPRange]
    asns: list[int]

@dataclass
class IPRange:
    range_type: Literal["ipv4", "ipv6", "combined"]
    ranges: list[str] | None = None
    last_updated: str | None = None  # ISO8601 date
    url: str | None = None
