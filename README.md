# CDN Mapping

## Example Format

```yaml
- name: AwesomeCDN
  homepage: https://www.awesomecdn.com
  domains:
    - awe.some
    - cdn.awesome
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
  asns:
    - 12345
    - 67890
  headers:
    - X-AwesomeCDN
    - X-AwesomeCDN-Edge
```

## References
- [TurboBytes CDN List](https://github.com/turbobytes/cdnfinder/blob/master/assets/cnamechain.json) ([MIT](https://github.com/turbobytes/cdnfinder/blob/master/LICENSE))
