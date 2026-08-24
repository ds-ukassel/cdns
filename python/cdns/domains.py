import re
from typing import List, Pattern


def compile_domains(domains: List[str]) -> Pattern:
    return re.compile('|'.join(domain2pattern(d) for d in domains), re.IGNORECASE)


def compile_domain(domain: str) -> Pattern:
    return re.compile(domain2pattern(domain), re.IGNORECASE)


def domain2pattern(domain: str) -> str:
    def replace(match: re.Match) -> str:
        token = match.group(0)
        if token == '**':
            return '.*'
        elif token == '*':
            return '[^.]+'
        elif token == '.':
            return r'\.'
        return token

    return '^' + re.sub(r'\*\*|\*|\.', replace, domain) + '$'
