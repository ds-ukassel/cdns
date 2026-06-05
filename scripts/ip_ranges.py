import json
import sys
from pathlib import Path
from typing import Any

import yaml
from requests import Session


def splitlines_ipv4(text: str) -> tuple[set[str], set[str]]:
    return set(text.splitlines()), set()


def splitline_ipv6(text: str) -> tuple[set[str], set[str]]:
    return set(), set(text.splitlines())


def splitline_combined(text: str) -> tuple[set[str], set[str]]:
    lines = text.splitlines()
    ipv4_ranges = set(line for line in lines if ":" not in line)
    ipv6_ranges = set(line for line in lines if ":" in line)
    return ipv4_ranges, ipv6_ranges


def amazon_cf_ipv4(text: str) -> tuple[set[str], set[str]]:
    data = json.loads(text)
    return set(data.get("CLOUDFRONT_GLOBAL_IP_LIST", []) + data.get("CLOUDFRONT_REGIONAL_EDGE_IP_LIST", [])), set()


def amazon_aws_combined(text: str) -> tuple[set[str], set[str]]:
    data = json.loads(text)
    return set(prefix["ip_prefix"] for prefix in data.get("prefixes", [])), set(
        prefix["ipv6_prefix"] for prefix in data.get("ipv6_prefixes", []))


def fastly_combined(text: str) -> tuple[set[str], set[str]]:
    data = json.loads(text)
    return set(data.get("addresses", [])), set(data.get("ipv6_addresses", []))

def imperva_combined(text: str) -> tuple[set[str], set[str]]:
    data = json.loads(text)
    return set(data.get("ipRanges", [])), set(data.get("ipv6Ranges", []))

def quiccloud_combined(text: str) -> tuple[set[str], set[str]]:
    prefixes = text.split("<br />")
    return set(prefix + "/32" for prefix in prefixes if ":" not in prefix), set(prefix + "/128" for prefix in prefixes if ":" in prefix)

def google_cloud_combined(text: str) -> tuple[set[str], set[str]]:
    data = json.loads(text)
    ipv4 = set(prefix["ipv4Prefix"] for prefix in data.get("prefixes", []) if "ipv4Prefix" in prefix)
    ipv6 = set(prefix["ipv6Prefix"] for prefix in data.get("prefixes", []) if "ipv6Prefix" in prefix)
    return ipv4, ipv6

CONVERTER = {
    "Cloudflare": (splitlines_ipv4, splitline_ipv6, None),
    "Amazon CloudFront": (amazon_cf_ipv4, None, None),
    "Amazon AWS": (None, None, amazon_aws_combined),
    "Fastly": (None, None, fastly_combined),
    "BunnyCDN": (None, None, splitline_combined),
    "Imperva": (None, None, imperva_combined),
    "CacheFly": (None, None, splitline_combined),
    "QUIC.cloud": (None, None, quiccloud_combined),
    "Google Cloud CDN": (None, None, google_cloud_combined),
    "Medianova": (None, None, splitline_combined),
}


def read_yaml(file_path: Path, default_value: Any = None) -> Any:
    """
    Reads a YAML file and returns its content.
    :param file_path: Path to the YAML file.
    :param default_value: Default value to return if an error occurs while reading the file.
    :return: Content of the YAML file or None if an error occurs.
    """
    with open(file_path) as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError:
            print(f"Error reading YAML file '{file_path}'.", file=sys.stderr)
            return default_value


def get_text_from_url(session: Session, url: str) -> str | None:
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching data from URL '{url}': {e}", file=sys.stderr)
        return None


def main():
    session = Session()

    cdns = read_yaml(Path(__file__).parent.parent / "cdns.yaml")
    if not cdns:
        sys.exit(1)

    for cdn in cdns:
        name = cdn.get("name")
        range_sources = cdn.get("ranges")
        if not range_sources:
            continue

        collected_ipv4_ranges = set()
        collected_ipv6_ranges = set()

        for source in range_sources:
            range_type = source["range_type"]

            if "url" in source:

                convert = CONVERTER.get(name)
                if not convert:
                    print(f"No converter found for CDN '{name}'.", file=sys.stderr)
                    continue

                convert_ip4, convert_ip6, convert_combined = convert

                text = get_text_from_url(session, source["url"])
                if text is None:
                    continue

                if range_type == "ipv4" and convert_ip4:
                    ipv4_ranges, _ = convert_ip4(text)
                    collected_ipv4_ranges.update(ipv4_ranges)
                elif range_type == "ipv6" and convert_ip6:
                    _, ipv6_ranges = convert_ip6(text)
                    collected_ipv6_ranges.update(ipv6_ranges)
                elif range_type == "combined" and convert_combined:
                    ipv4_ranges, ipv6_ranges = convert_combined(text)
                    collected_ipv4_ranges.update(ipv4_ranges)
                    collected_ipv6_ranges.update(ipv6_ranges)

            elif "ranges" in source:
                ranges = source["ranges"]
                if range_type == "ipv4":
                    collected_ipv4_ranges.update(ranges)
                elif range_type == "ipv6":
                    collected_ipv6_ranges.update(ranges)


        for ip_range in sorted(collected_ipv4_ranges):
            print(f"{name}\t{ip_range}\tipv4")

        for ip_range in sorted(collected_ipv6_ranges):
            print(f"{name}\t{ip_range}\tipv6")

    session.close()


if __name__ == "__main__":
    main()
