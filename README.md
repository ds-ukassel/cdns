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
      last_updated: 1970-01-01
  asns:
    - 12345
    - 67890
  headers:
    - X-AwesomeCDN:         # 'X-AwesomeCDN' header must be present
    - Server: AwesomeCDN    # 'Server' header must contain 'AwesomeCDN'
    - X-Cache: HIT          # 'X-Cache' header must contain 'HIT' and 'X-Whatever' header must be present
      X-Whatever:           
```

## References
- [TurboBytes CDN List](https://github.com/turbobytes/cdnfinder/blob/master/assets/cnamechain.json) ([MIT](https://github.com/turbobytes/cdnfinder/blob/master/LICENSE))
- [CDNProbe 'cname cache'](https://github.com/njuzmy/CDNProbe/blob/main/assets/static/cdn/cname_cache.json) ([Apache 2.0](https://github.com/njuzmy/CDNProbe/blob/main/LICENSE))
  - Parts of their CNAME substring list was used to expand our own list.
- [CDN Handbook](https://www.cdnhandbook.com/)
  - Information about some CDNs
