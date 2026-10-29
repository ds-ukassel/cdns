# CDN Mapping

Provides a JS library [`@ds-ukassel/cdns`](https://www.npmjs.com/package/@ds-ukassel/cdns) and Python library [`cdns`](https://pypi.org/project/cdns/) to identify CDNs.
All CDNs are listed in [`cdns.yaml`](cdns.yaml) in this repository, and [`dist/cdns.json`](dist/cdns.json) in the package.

## YAML Format

```yaml
- name: AwesomeCDN
  homepage: https://www.awesomecdn.com
  type: commercial
  domains: # See "Domain patterns" below
    - 'awesomecdn.com'      # 'awesomecdn.com' is a full match of the domain (e.g. 'awesomecdn.com')
    - '**awesomecdn**'      # 'awesomecdn' is a substring of the domain (e.g. 'a.awessomecdn.com')
    - '*.cdn.awesome.com'   # '*' is a wildcard for a single domain level (e.g. 'a.cdn.awesome.com' or 'b.cdn.awesome.com')
    - '**.awesomecdn.*'     # '**' is a wildcard for one or more domain levels (e.g. 'a.b.awesomecdn.de' or 'c.d.e.awesomecdn.com')
  ranges:
    - range_type: 'ipv4'
      url: 'https://api.awesomecdn.com/ips-v4/'
    - range_type: 'ipv6'
      url: 'https://api.awesomecdn.com/ips-v6/'
    - range_type: 'combined'
      url: 'https://api.awesomecdn.com/ips/'
    - range_type: 'ipv4'
      ranges:
        - '111.111.111.111/32'
      last_updated: 1970-01-01
  asns:
    - 12345
    - 67890
  headers: # See "Header Patterns" below
    - X-AwesomeCDN:         # 'X-AwesomeCDN' header must be present
    - Server: AwesomeCDN    # 'Server' header must contain 'AwesomeCDN'
    - X-Cache: HIT          # 'X-Cache' header must contain 'HIT'
      X-Whatever:           # AND 'X-Whatever' header must be present
```

## Domain Wildcard Syntax
When implementing the wildcard syntax for domains, the following rules apply:
- `*` matches a single domain level
  - `*.example.com` matches `abc.example.com` 
  - `*.example.com` does **not** match `abc.def.example.com`
- `**` matches one or more domain levels or any prefix 
  - `**.example.com` matches `a.example.com` and `b.c.example.com`
  - `**example.com` matches `example.com`, `a.example.com`, and `b.c.example.com`


`*` and `**` can appear anywhere in the domain string, including the beginning, middle, or end.

### Regex Equivalents
- `*` is equivalent to `[^.]+` (matches any character except dots, one or more times)
- `**` is equivalent to `.*` (matches any character, including dots, zero or more times)


- All special characters are escaped, e.g. `.` turns into `\.`.
- The regex receives the prefix `^` and suffix `$`.

#### Examples

- `**example.com` -> `^.*example\.com$`
- `*.example.com` -> `^[^.]+\.example\.com$`

## Header Patterns

Header patterns have a few rules:
- `Header:` (JSON: `{"Header": null}`) means the header must be present, but can have any value.
- `Header: foo` (JSON: `{"Header": "foo"}`) means the header must be present and equal the value.
- Multiple patterns in the same entry, e.g.
  ```yaml
  Header-1:
  Header-2: bar
  ```
  or JSON: `{"Header-1": null, "Header-2": "bar"}`
  Means ALL header patterns must match.
- Header keys are case-insensitive, but values are case-sensitive.

The values can use `*` as a wildcard for any number of characters, e.g. `foo*` matches `foo`, `foobar`, and `foo123`.
Any amount of `*` can be used at different positions.

To use a literal `*`, escape it with a backslash: `\*`.

## Types

Each CDN can have a designated `type` field.
The type can either be `commercial`, `private`, `public_assets` or `other`.

- `commercial`: CDNs used by different customers (e.g. Akamai, Fastly, ...)
- `private`: CDNs used internally by a single company (e.g. Meta, Instagram, ...)
- `public_assets`: CDNs providing public assets not uploaded by customers (e.g. BootstrapCDN)
- `other`: CDNs with an entirely different model

The field is optional as this information isn't always available/clear.

## Python API

```python
def compile_domains(domains: list[str]) -> Pattern:
    ...
def compile_domain(domain: str) -> Pattern:
    ...
```

([source](python/cdns/domains.py)):
Compile domain patterns to a RegExp according to the [Domain Pattern rules](#regex-equivalents).

```python
def matches(headers: Dict[str, str], matcher: Dict[str, Optional[str]]) -> bool:
    ...
def match_headers(headers: Dict[str, str], matchers: List[Dict[str, Optional[str]]]) -> Dict[str, str]:
    ...
```

([source](python/cdns/headers.py)):
Match response headers against the patterns according to the [Header Pattern rules](#header-patterns).

## TS API

```ts
function compileDomains(domains: string[]): RegExp
function compileDomain(domain: string): RegExp
```
([source](src/domains.ts)):
Compile domain patterns to a RegExp according to the [Domain Pattern rules](#regex-equivalents).

```ts
function matchHeaders(headers: Record<string, string>, patterns: Record<string, string | null>[]
```
([source](src/headers.ts)):
Match response headers against the patterns according to the [Header Pattern rules](#header-patterns).

## References
- [TurboBytes CDN Finder](https://github.com/turbobytes/cdnfinder) ([MIT](https://github.com/turbobytes/cdnfinder/blob/master/LICENSE))
  - [CNAME Chain](https://github.com/turbobytes/cdnfinder/blob/master/assets/cnamechain.json)
- [CDNProbe](https://github.com/njuzmy/CDNProbe) ([Apache 2.0](https://github.com/njuzmy/CDNProbe/blob/main/LICENSE))
  - [cname_cache](https://github.com/njuzmy/CDNProbe/blob/main/assets/static/cdn/cname_cache.json): Parts of the substring list were used to extend our own list
  - [cdnlist](https://github.com/njuzmy/CDNProbe/blob/main/assets/static/cdn/cdnlist.txt): Some CDNs from the cdn list were used to extend our own list
- [CDN Handbook](https://www.cdnhandbook.com/)
  - Information about some CDNs
- [IPInfo](https://ipinfo.io/)
  - Information about ASNs used by CDNs
- [CDN-CNAME-Domain](https://github.com/u9sky/cdn-cname-domain/blob/main/cdn.yml)
- [cdn-ip-database](https://github.com/mansourjabin/cdn-ip-database) ([MIT](https://github.com/mansourjabin/cdn-ip-database/blob/main/LICENSE))
  - [sources.json](https://github.com/mansourjabin/cdn-ip-database/blob/main/data/sources.json)
- [Third Party Web](https://github.com/patrickhulce/third-party-web) ([MIT](https://github.com/patrickhulce/third-party-web/blob/master/LICENSE))
  - [entities.json](https://github.com/patrickhulce/third-party-web/blob/master/data/entities.js)
- [ProjectDiscovery cdncheck](https://github.com/projectdiscovery/cdncheck) ([MIT](https://github.com/projectdiscovery/cdncheck/blob/main/LICENSE.md))
  - [provider.yaml](https://github.com/projectdiscovery/cdncheck/blob/main/cmd/generate-index/provider.yaml)
- [Netify](https://www.netify.ai/resources/cdn)
- Behnam Shobiri, Mohammad Mannan, and Amr Youssef. 2023. CDNs’ Dark Side: Security Problems in CDN-to-Origin Connections. Digital Threats 4, 1, Article 3 (March 2023), 22 pages. https://doi.org/10.1145/3499428

## License
Original content created by members of the Distributed Systems Group is licensed under the  [MIT license](LICENSE).
The information compiled in this repository has in part be collected from publicly available repositories and is intended for research purposes.
Content created by third parties remains subject to its respective license.
Please respect the original licensing terms and provide appropriate attribution when using or redistributing third party content.
See our [references ](#references) for more information.
