import {describe, expect, it} from 'vitest';
import {matches, matchHeaders, header2pattern} from './headers.js';

describe('matches', () => {
  it('returns true when all headers match exactly', () => {
    const headers = {'content-type': 'text/html'};
    const matcher = {'content-type': 'text/html'};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('returns true for partial match (header not in response)', () => {
    const headers = {'content-type': 'text/html', 'x-powered-by': 'Express'};
    const matcher = {'content-type': 'text/html'};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('returns false when a header value differs', () => {
    const headers = {'content-type': 'text/html'};
    const matcher = {'content-type': 'application/json'};
    expect(matches(headers, matcher)).toBe(false);
  });

  it('handles null expected value (header must be present)', () => {
    const headers = {'content-type': 'text/html'};
    const matcher = {'x-custom-header': null};
    expect(matches(headers, matcher)).toBe(false);
  });

  it('returns true when header with null expected is present', () => {
    const headers = {'x-custom-header': 'exists'};
    const matcher = {'x-custom-header': null};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('handles lowercase headers from responses (keys must be lowercase)', () => {
    const headers = {'content-type': 'text/html'};
    const matcher = {'content-type': 'text/html'};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('returns false when header key mismatch causes lookup to fail', () => {
    const headers = {'Content-Type': 'text/html'};
    const matcher = {'x-powered-by': 'Express'};
    expect(matches(headers, matcher)).toBe(false);
  });

  it('returns true for empty matcher', () => {
    const headers = {'content-type': 'text/html'};
    const matcher: Record<string, string | null> = {};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('handles multiple matchers with null values', () => {
    const headers = {'x-header-a': 'any', 'x-header-b': 'value'};
    const matcher = {'x-header-a': null, 'x-header-b': null};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('returns false if any header with null expected is absent', () => {
    const headers = {'x-header-a': 'present'};
    const matcher = {'x-header-a': null, 'x-header-b': null};
    expect(matches(headers, matcher)).toBe(false);
  });

  it('handles missing header value with non-null expected', () => {
    const headers: Record<string, string> = {};
    const matcher = {'content-type': 'text/html'};
    expect(matches(headers, matcher)).toBe(false);
  });

  it('returns true if a wildcard is used', () => {
    const headers = {'x-header-a': 'value-a'};
    const matcher = {'x-header-a': 'value-*'};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('returns true if multiple wildcards are used', () => {
    const headers = {'x-header-a': 'value-a-b-c'};
    const matcher = {'x-header-a': 'value-*-*-c'};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('returns true if an escaped asterisk is used', () => {
    const headers = {'x-header-a': 'value-*'};
    const matcher = {'x-header-a': 'value-\\*'};
    expect(matches(headers, matcher)).toBe(true);
  });

  it('returns false if an escaped asterisk is used with an incorrect value', () => {
    const headers = {'x-header-a': 'value-a'};
    const matcher = {'x-header-a': 'value-\\*'};
    expect(matches(headers, matcher)).toBe(false);
  });

  it('returns false if the case is incorrect', () => {
    const headers = {'x-header-a': 'value-a'};
    const matcher = {'x-header-a': 'value-A'};
    expect(matches(headers, matcher)).toBe(false);
  });
});

describe('matchHeaders', () => {
  it('returns matching headers for a single matching matcher', () => {
    const headers = {'content-type': 'text/html', 'server': 'nginx'};
    const matchers = [{'content-type': 'text/html'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({'content-type': 'text/html'});
  });

  it('returns empty object when no matcher matches', () => {
    const headers = {'content-type': 'text/html'};
    const matchers = [{'content-type': 'application/json'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({});
  });

  it('collects keys from all matching matchers', () => {
    const headers = {'content-type': 'text/html', 'server': 'nginx', 'x-powered-by': 'Express'};
    const matchers = [
      {'content-type': 'text/html'},
      {'server': 'nginx'},
    ];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({
      'content-type': 'text/html',
      'server': 'nginx',
    });
  });

  it('returns empty object when some matchers match and others do not', () => {
    const headers = {'content-type': 'text/html', 'server': 'apache'};
    const matchers = [
      {'content-type': 'text/html'},
      {'server': 'nginx'},
    ];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({'content-type': 'text/html'});
  });

  it('omits headers with undefined values when null expected', () => {
    const headers: Record<string, string> = {};
    const matchers = [{'x-custom': null}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({'x-custom': undefined});
  });

  it('handles multiple matchers with overlapping keys', () => {
    const headers = {'content-type': 'text/html'};
    const matchers = [
      {'content-type': 'text/html'},
      {'content-type': 'text/html'},
    ];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({'content-type': 'text/html'});
  });

  it('is case-sensitive for header keys (keys must be lowercase)', () => {
    const headers = {'Content-Type': 'text/html'};
    const matchers = [{'content-type': 'text/html'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({});
  });

  it('handles empty headers object', () => {
    const headers: Record<string, string> = {};
    const matchers = [{'content-type': 'text/html'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({});
  });

  it('handles empty matchers array', () => {
    const headers = {'content-type': 'text/html'};
    const matchers: Record<string, string | null>[] = [];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({});
  });

  it('handles empty matcher object within matchers', () => {
    const headers = {'content-type': 'text/html'};
    const matchers: Record<string, string | null>[] = [{}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({});
  });

  it('collects headers from overlapping keys across different matching matchers', () => {
    const headers = {'content-type': 'text/html', 'server': 'nginx'};
    const matchers = [
      {'content-type': 'text/html', 'server': 'nginx'},
    ];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({
      'content-type': 'text/html',
      'server': 'nginx',
    });
  });

  it('returns headers with null matched values as undefined from response', () => {
    const headers = {'x-custom': 'value'};
    const matchers = [{'x-custom': 'value'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({'x-custom': 'value'});
  });

  it('handles matcher with both null and non-null expected values', () => {
    const headers: Record<string, string> = {};
    const matchers = [{'content-type': 'text/html', 'x-absent': null}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({});
  });

  it('matches when all keys in matcher are present and match', () => {
    const headers = {'a': '1', 'b': '2'};
    const matchers = [{'a': '1', 'b': '2'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({a: '1', b: '2'});
  });

  it('does not match when extra headers exist beyond matcher expectations', () => {
    const headers = {'content-type': 'text/html', 'server': 'nginx', 'x-extra': 'data'};
    const matchers = [{'content-type': 'text/html', 'server': 'nginx'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({
      'content-type': 'text/html',
      'server': 'nginx',
    });
  });

  it('handles null value with non-matching key in other matcher', () => {
    const headers: Record<string, string> = {};
    const matchers = [{'x-absent': null}, {'content-type': 'text/html'}];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({'x-absent': undefined});
  });

  it('overwrites value when same key appears in multiple matching matchers', () => {
    const headers = {'content-type': 'text/html'};
    const matchers = [
      {'content-type': 'text/html'},
      {'content-type': 'text/html'},
      {'content-type': 'text/html'},
    ];
    const result = matchHeaders(headers, matchers);
    expect(result).toEqual({'content-type': 'text/html'});
  });
});

describe('header2pattern', () => {
  it('returns the correct value without any wildcards', () => {
    expect(header2pattern("abc")).toEqual(RegExp("^abc$"))
  })

  it('returns the correct value with a wildcard', () => {
    expect(header2pattern("a*c")).toEqual(RegExp("^a.*c$"))
  })


  it('returns the correct value with an escaped asterisk', () => {
    expect(header2pattern("a\\*c")).toEqual(RegExp("^a\\*c$"))
  })


  it('returns the correct value with regex characters', () => {
    expect(header2pattern("a.+?^$|()[]{}c")).toEqual(RegExp("^a\\.\\+\\?\\^\\$\\|\\(\\)\\[\\]\\{\\}c$"))
  })
});
