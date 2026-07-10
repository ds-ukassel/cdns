import {describe, expect, it} from 'vitest';
import {compileDomain, compileDomains} from './domains.js';

describe('compileDomain', () => {
  it('matches an exact domain', () => {
    const pattern = compileDomain('example.com');
    expect(pattern.test('example.com')).toBe(true);
    expect(pattern.test('EXAMPLE.COM')).toBe(true);
    expect(pattern.test('another.com')).toBe(false);
  });

  it('matches subdomains with single wildcard', () => {
    const pattern = compileDomain('*.example.com');
    expect(pattern.test('cdn.example.com')).toBe(true);
    expect(pattern.test('static.example.com')).toBe(true);
    expect(pattern.test('example.com')).toBe(false);
  });

  it('does not match double subdomain with single wildcard', () => {
    const pattern = compileDomain('*.example.com');
    expect(pattern.test('a.b.example.com')).toBe(false);
  });

  it('is case-insensitive', () => {
    const pattern = compileDomain('Example.Com');
    expect(pattern.test('example.com')).toBe(true);
    expect(pattern.test('EXAMPLE.COM')).toBe(true);
    expect(pattern.test('eXaMpLe.CoM')).toBe(true);
  });

  it('escapes dots in domain', () => {
    const pattern = compileDomain('sub.example.com');
    expect(pattern.test('subexample.com')).toBe(false);
    expect(pattern.test('subxexample.com')).toBe(false);
    expect(pattern.test('sub.example.com')).toBe(true);
  });

  it('matches only the exact domain without suffix', () => {
    const pattern = compileDomain('test.org');
    expect(pattern.test('test.org')).toBe(true);
    expect(pattern.test('test.org.evil.com')).toBe(false);
    expect(pattern.test('mytest.org')).toBe(false);
  });

  it('matches wildcard with literal asterisk strings', () => {
    const pattern = compileDomain('**.example.com');
    // `**` at start becomes `.*`, so the final pattern is `^.*\.example\.com$`.
    // `.*` can match literal `**`, so "**.example.com" matches as well.
    expect(pattern.test('**' + '.example.com')).toBe(true);
  });

  it('matches wildcard before domain without leading dot', () => {
    const pattern = compileDomain('**example.com');
    expect(pattern.test('**example.com')).toBe(true);
  });

  it('handles single wildcard in middle of domain', () => {
    const pattern = compileDomain('cdn.*.com');
    expect(pattern.test('cdn.example.com')).toBe(true);
    expect(pattern.test('cdn.cdn2.com')).toBe(true); // [^.]+ matches 'cdn2' before the escaped dot
  });

  it('handles single wildcard at end of domain', () => {
    const pattern = compileDomain('example.*');
    expect(pattern.test('example.com')).toBe(true);
    expect(pattern.test('example.net')).toBe(true);
    expect(pattern.test('example.cdn.wow')).toBe(false); // [^.]+ only matches one segment
  });
});

describe('compileDomains', () => {
  it('matches any of the provided domains', () => {
    const pattern = compileDomains(['cloudflare.com', 'akamai.net']);
    expect(pattern.test('cloudflare.com')).toBe(true);
    expect(pattern.test('akamai.net')).toBe(true);
    expect(pattern.test('example.org')).toBe(false);
  });

  it('works with single wildcard', () => {
    const pattern = compileDomains(['*.cdn.example.com']);
    expect(pattern.test('a.cdn.example.com')).toBe(true);
    expect(pattern.test('b.cdn.example.com')).toBe(true);
    expect(pattern.test('cdn.example.com')).toBe(false);
  });

  it('combines exact domains and wildcards', () => {
    const pattern = compileDomains(['exact.com', '*.wild.example.com']);
    expect(pattern.test('exact.com')).toBe(true);
    expect(pattern.test('sub.wild.example.com')).toBe(true);
    expect(pattern.test('other.com')).toBe(false);
  });

  it('is case-insensitive across all domains', () => {
    const pattern = compileDomains(['Example.com']);
    expect(pattern.test('example.com')).toBe(true);
    expect(pattern.test('EXAMPLE.COM')).toBe(true);
  });

  it('matches everything with empty array (empty regex pattern)', () => {
    const pattern = compileDomains([]);
    // Empty domains produces RegExp('', 'i') which matches everything
    expect(pattern.test('')).toBe(true);
    expect(pattern.test('anything.com')).toBe(true);
  });

  it('escapes dots in wildcard domains', () => {
    const pattern = compileDomain('*.examplecom');
    // Pattern is ^[^.]+\\.examplecom$ - dot after wildcard is escaped, cdn.examplecom matches
    expect(pattern.test('cdn.examplecom')).toBe(true);
    expect(pattern.test('cdnexamplecom')).toBe(false);
  });
});
