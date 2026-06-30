import json
import re
from abc import ABC, abstractmethod
from typing import TypeAlias

from requests import Session
from bs4 import BeautifulSoup

from ranges import utils

IPResult: TypeAlias = tuple[set[str], set[str]]


class Parser(ABC):

    @staticmethod
    def fetch(url: str, session: Session) -> str:
        return utils.fetch(url, session)

    @staticmethod
    @abstractmethod
    def parse(content: str) -> IPResult:
        ...


class MicrosoftParser(Parser):

    @staticmethod
    def fetch(url: str, session: Session) -> str:
        # Download the html page
        html = utils.fetch(url, session)

        # Search for download link
        match = re.search(r"https://download\.microsoft\.com/download/.+?/ServiceTags_Public_\d+\.json", html)
        if not match:
            raise ValueError("Could not find Microsoft IP ranges download link.")
        download_url = match.group(0)

        # Download the actual file
        return utils.fetch(download_url, session)

    @staticmethod
    def parse(content: str) -> IPResult:
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


class SplitLinesParser(Parser):
    @staticmethod
    def parse(content: str):
        return (
            {line for line in content.splitlines() if ":" not in line},
            {line for line in content.splitlines() if ":" in line},
        )


class AmazonAWSParser(Parser):
    @staticmethod
    def parse(content: str):
        data = json.loads(content)
        ipv4 = {prefix["ip_prefix"] for prefix in data.get("prefixes", []) if "ip_prefix" in prefix}
        ipv6 = {prefix["ipv6_prefix"] for prefix in data.get("prefixes", []) if "ipv6_prefix" in prefix}
        return ipv4, ipv6


class AmazonCFParser(Parser):
    @staticmethod
    def parse(content: str):
        data = json.loads(content)
        return set(data.get("CLOUDFRONT_GLOBAL_IP_LIST", []) + data.get("CLOUDFRONT_REGIONAL_EDGE_IP_LIST", [])), set()


class FastlyParser(Parser):
    @staticmethod
    def parse(content: str):
        data = json.loads(content)
        return set(data.get("addresses", [])), set(data.get("ipv6_addresses", []))


class ImpervaParser(Parser):
    @staticmethod
    def parse(content: str):
        data = json.loads(content)
        return set(data.get("ipRanges", [])), set(data.get("ipv6Ranges", []))


class QuicCloudParser(Parser):
    @staticmethod
    def parse(content: str):
        prefixes = content.split("<br />")
        ipv4 = set(prefix + "/32" for prefix in prefixes if ":" not in prefix)
        ipv6 = set(prefix + "/128" for prefix in prefixes if ":" in prefix)
        return ipv4, ipv6


class GoogleCloudParser(Parser):
    @staticmethod
    def parse(content: str):
        data = json.loads(content)
        ipv4 = set(prefix["ipv4Prefix"] for prefix in data.get("prefixes", []) if "ipv4Prefix" in prefix)
        ipv6 = set(prefix["ipv6Prefix"] for prefix in data.get("prefixes", []) if "ipv6Prefix" in prefix)
        return ipv4, ipv6


class SucuriParser(Parser):
    @staticmethod
    def parse(content: str):
        soup = BeautifulSoup(content, "html.parser")

        ipv4 = set()
        ipv6 = set()

        error = soup.find("strong", string="502 Errors")
        if not error:
            raise ValueError("Could not find '502 Errors' section in Sucuri page.")
        code_block = error.find_next("code")
        if not code_block:
            raise ValueError("Could not find code block after '502 Errors' section in Sucuri page.")
        for line in code_block.get_text().splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                ipv6.add(line)
            else:
                ipv4.add(line)
        return ipv4, ipv6


class OVHParser(Parser):
    @staticmethod
    def parse(content: str):
        soup = BeautifulSoup(content, "html.parser")

        ipv4 = set()
        ipv6 = set()

        table = soup.find("table")
        if not table:
            raise ValueError("Could not find 'Adresse IP' table in OVH page.")
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            for cell in cells:
                cell_text = cell.get_text().strip()
                if not cell_text:
                    continue
                if ":" in cell_text:
                    ipv6.add(cell_text)
                else:
                    ipv4.add(cell_text)
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
    "Microsoft Azure CDN": MicrosoftParser,
    "Sucuri": SucuriParser,  # Currently unused because of 503
    "OVH CDN": OVHParser,
}
