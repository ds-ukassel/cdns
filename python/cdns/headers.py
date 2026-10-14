import re
from typing import Dict, List, Optional


def match_headers(
    headers: Dict[str, str],
    matchers: List[Dict[str, Optional[str]]],
) -> Dict[str, str]:
    """
    Matches the given response headers against the CDN header matchers.

    :param headers: the response headers. Keys must be lowercase.
    :param matchers: the CDN header matchers.
    :return: all matching headers from the response headers.
        If this dict is empty, no matchers matched the response headers.
    """
    result: Dict[str, str] = {}
    for matcher in matchers:
        if not matches(headers, matcher):
            continue
        for key in matcher.keys():
            result[key] = headers[key.lower()]
    return result


def matches(headers: Dict[str, str], matcher: Dict[str, Optional[str]]) -> bool:
    """
    Checks if the given response headers match the given CDN header matcher.

    :param headers: the response headers. Keys must be lowercase.
    :param matcher: the CDN header matcher.
    :return: True if the response headers match the CDN header matcher, False otherwise.
    """
    for key, expected_value in matcher.items():
        header_value = headers.get(key.lower())
        if expected_value is None:  # any value is acceptable
            if header_value is None:
                return False
        elif not value_matches(header_value, expected_value):
            return False
    return True


def value_matches(header_value: Optional[str], expected_value: str) -> bool:
    if header_value is None:
        return False
    if "*" in expected_value:
        pattern = header2pattern(expected_value)
        return re.fullmatch(pattern, header_value) is not None
    return header_value == expected_value


def header2pattern(header: str) -> str:
    def replace(match: re.Match) -> str:
        token = match.group(0)
        if token == "*":
            return ".*"
        elif token == "\\*":
            return token
        else:
            return "\\" + token
    return "^" + re.sub(r'\\\*|\*|\.|\+|\?|\^|\$|\||\\|\(|\)|\[|\]|\{|\}', replace, header) + "$"
