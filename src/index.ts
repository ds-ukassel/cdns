import _cdns from './cdns.json' with {type: 'json'};

export interface CDN {
  name: string;
  homepage?: string;
  domains?: string[];
  headers?: Record<string, string | null>[];
  asns?: number[];
  ranges?: IPRange[];
}

export interface IPRange {
  range_type: 'ipv4' | 'ipv6' | 'combined';
  ranges?: string[];
  last_updated?: string; // ISO8601 date
  url?: string;
}

export const cdns: CDN[] = _cdns;
export * from './domains.js';
export * from './headers.js';
