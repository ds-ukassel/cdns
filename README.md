# CDN Mapping

## Example Format

```yaml
- name: AwesomeCDN
  homepage: https://www.awesomecdn.com
  domains:
    - awesomecdn           # 'awesomecdn' is a substring of the CNAME (e.g. 'a.awessomecdn.com')
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

## Wildcard Syntax
When implementing the wildcard syntax, the following rules apply:
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
