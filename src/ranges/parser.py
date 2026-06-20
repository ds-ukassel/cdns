import json
import re
from abc import ABC, abstractmethod
from typing import TypeAlias

from requests import Session

from ranges.utils import fetch

IPResult: TypeAlias = tuple[set[str], set[str]]


class Parser(ABC):

    @staticmethod
    @abstractmethod
    def parse(url: str, session: Session) -> IPResult:
        ...


class MicrosoftParser(Parser):

    @staticmethod
    def _parse_ranges(content: str) -> IPResult:
        ipv4_ranges = set()
        ipv6_ranges = set()

        data = json.loads(content)
        for entry in data.get("values", []):
            for prefix in entry.get("properties", {}).get("addressPrefixes", []):
                if ":" in prefix:
                    ipv6_ranges.add(prefix)
                else:
                    ipv4_ranges.add(prefix)

        return ipv4_ranges, ipv6_ranges

    def parse(self, url: str, session: Session) -> IPResult:
        html = fetch(session, url)

        # Search for link starting with 'https://download.microsoft.com/download'
        match = re.search(r'https://download\.microsoft\.com/download[^\s"]]+', html)
        if not match:
            raise ValueError("Could not find Microsoft IP ranges download link.")
        download_url = match.group(0)

        # Download the file
        file_response = session.get(download_url)
        file_response.raise_for_status()

        # Parse the file content
        return self._parse_ranges(file_response.text)


class SplitLinesParser(Parser):
    @staticmethod
    def parse(url: str, session: Session):
        data = fetch(session, url)
        return (
            {line for line in data.splitlines() if ":" not in line},
            {line for line in data.splitlines() if ":" in line},
        )


class AmazonAWSParser(Parser):
    @staticmethod
    def parse(url: str, session: Session):
        data = json.loads(fetch(session, url))
        ipv4 = {prefix["ip_prefix"] for prefix in data.get("prefixes", []) if "ip_prefix" in prefix}
        ipv6 = {prefix["ipv6_prefix"] for prefix in data.get("prefixes", []) if "ipv6_prefix" in prefix}
        return ipv4, ipv6


class AmazonCFParser(Parser):
    @staticmethod
    def parse(url: str, session: Session):
        data = json.loads(fetch(session, url))
        return set(data.get("CLOUDFRONT_GLOBAL_IP_LIST", []) + data.get("CLOUDFRONT_REGIONAL_EDGE_IP_LIST", [])), set()


class FastlyParser(Parser):
    @staticmethod
    def parse(url: str, session: Session):
        data = json.loads(fetch(session, url))
        return set(data.get("addresses", [])), set(data.get("ipv6_addresses", []))


class ImpervaParser(Parser):
    @staticmethod
    def parse(url: str, session: Session):
        data = json.loads(fetch(session, url))
        return set(data.get("ipRanges", [])), set(data.get("ipv6Ranges", []))


class QuicCloudParser(Parser):
    @staticmethod
    def parse(url: str, session: Session):
        prefixes = fetch(session, url).split("<br />")
        ipv4 = set(prefix + "/32" for prefix in prefixes if ":" not in prefix)
        ipv6 = set(prefix + "/128" for prefix in prefixes if ":" in prefix)
        return ipv4, ipv6


class GoogleCloudParser(Parser):
    @staticmethod
    def parse(url: str, session: Session):
        data = json.loads(fetch(session, url))
        ipv4 = set(prefix["ipv4Prefix"] for prefix in data.get("prefixes", []) if "ipv4Prefix" in prefix)
        ipv6 = set(prefix["ipv6Prefix"] for prefix in data.get("prefixes", []) if "ipv6Prefix" in prefix)
        return ipv4, ipv6


PARSERS = {
    "Cloudflare": SplitLinesParser,
    "Amazon CloudFront": AmazonCFParser,
    "Amazon AWS": AmazonAWSParser,
    "Fastly": FastlyParser,
    "BunnyCDN": SplitLinesParser,
    "Imperva": ImpervaParser,
    "CacheFly": SplitLinesParser,
    "QuicCloud": QuicCloudParser,
    "Google Cloud": GoogleCloudParser,
    "Medianova": SplitLinesParser,
    "Microsoft": MicrosoftParser,
}
