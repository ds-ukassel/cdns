import json


def convert_amazon_cloudfront(text: str) -> set[str]:
    data = json.loads(text)
    return set(data.get("CLOUDFRONT_GLOBAL_IP_LIST", []) + data.get("CLOUDFRONT_REGIONAL_EDGE_IP_LIST", []))

def convert_amazon_aws(text: str) -> list[str]:
    data = json.loads(text)
    return [prefix["ip_prefix"] for prefix in data.get("prefixes", [])]

CONVERTER = {
    "Cloudflare": lambda text: text.splitlines(),
    "Amazon CloudFront": convert_amazon_cloudfront,
    "Amazon AWS": convert_amazon_aws,
}
