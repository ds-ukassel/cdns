# CDN Mapping

## Example Format

```yaml
- name: AwesomeCDN
  homepage: https://www.awesomecdn.com
  domains:
    - awe.some
    - cdn.awesome
  ranges:
    ipv4:
      - https://ip-ranges.awesomecdn.com/ipv4.txt
    ipv6:
      - https://ip-ranges.awesomecdn.com/ipv6.txt
  asns:
    - 12345
    - 67890
  headers:
    - X-AwesomeCDN
    - X-AwesomeCDN-Edge
```
